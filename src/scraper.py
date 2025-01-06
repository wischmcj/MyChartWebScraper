import requests
import itertools
from datetime import datetime, time 
from calendar import month_name

import re
from dataclasses import dataclass

from log_utils import log
from gsheets import gsheets_export

#medicine for morning (1), afternoon (2), ...
#https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=1&cat=999&dat=
#https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=2&cat=999&dat=

# Day at a glace 
#https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&sch=66879

# Day at a glance - yesterday as of 2024/02/12 

# https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&sch=66881


from bs4 import BeautifulSoup

URL = "https://mychart.emoryhealthcare.org/mychart-prd/Authentication/Login/" 
 
post_url  = "https://mychart.emoryhealthcare.org/MyChart-prd/Authentication/Login/DoLogin"


@dataclass
class Medication:
    generic_name: str
    brand_name: str
    modality: str
    raw: str = None

    def transform_if_applicable(self, med_dict:dict):
        for raw_data in med_dict.keys():
            if self.raw.lower() == raw_data.lower():
                self.name = med_dict[raw_data][0]
                self.modality = med_dict[raw_data][1]
                self.dosage = med_dict[raw_data][2]
                self.dosage_unit = med_dict[raw_data][3]
            else:
                pass
        return self

@dataclass
class Dose:
    # medicine_id: str
    quantity: str
    unit: str
    date: datetime
    dose_time: str
    ips: bool = False
    ivpb: bool = False
    omnicell_override_pull: bool = False
    dosed_medication: str = None
    url: str = None
    time_of_day:str = None


@dataclass
class Joined:
    generic_name: str = None
    brand_name: str= None
    modality: str= None
    quantity: str= None
    unit: str= None
    date: datetime= None
    dose_time: time = None
    ips: bool = False
    ivpb: bool = False
    omnicell_override_pull: bool = False
    raw_sched_row:str = None
    time_of_day:str = None
    
    def __init__(self,med:Medication,dose:Dose):
        self.generic_name = med.generic_name
        self.brand_name = med.brand_name    
        self.modality = med.modality
        self.quantity = dose.quantity
        self.unit = dose.unit
        self.date = dose.date
        self.dose_time = dose.dose_time
        self.ips = dose.ips
        self.ivpb = dose.ivpb
        self.omnicell_override_pull = dose.omnicell_override_pull
        self.raw_sched_row = med.raw
        self.url = dose.url
        self.time_of_day = dose.time_of_day

@dataclass
class Treatment:
    frequency: str
    start_date: str
    end_date: str
    instructions: str
    side_effects: str


login_info = {"Type":"StandardLogin","Credentials":{"Username":os.environ['MY_CHART_USER64'],"Password":os.environ['MY_CHART_PASS64']}}
Device_id = "WEB,276a0198b48a4741b8d6b2605db47678,1QeY2eV4+nFGmxvY5KaPAkBfr5BA/NN6H9Kdku6KeZM="
login_info = '{"Type":"StandardLogin","Credentials":{"Username":"","Password":""}}'
medication_url = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&sch=66878'
itinerary_url = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary'

given_Day_meds = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=1&cat=999&dat=66878'

funky_meds = {
        # 'Cellcept': ('mycophenolate (Cellcept)', '200mg/ml suspension', '500', 'mg'),
        # 'Duo-Neb':  ('ipratropium-albuterol (Duo-Neb)', '0.5mg-3mg/3ml solution', '3', 'ml'),
        # 'AndroGel': ('testosterone (AndroGel)', '50mg/5 gram (1 %) gel', '50', 'mg'),
        # 'Lidoderm': ('lidocaine (Lidoderm)', '5% patch', '1', 'patch')
        #   Medication(name='', modality='sodium chloride', dosage='0.9',
        #    dosage_unit='% infusion  - Omnicell Override Pull', time=None)]
        #
        '' : ('', '', '', '')
}


def build_glance_urls(cat = '999', date_codes= [''], tods:list[str] = ['1','2','3','4','5'] ):
    urls = ['']*len(tods)*len(date_codes)
    for idy, dat in enumerate(date_codes):
        for idx, tod in enumerate(tods):
            med_url = f'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod={tod}&cat={cat}&dat={dat}'
            referer_url = f'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&sch={dat}' 
            urls[idx*len(date_codes) + idy] = (med_url, referer_url)
    return urls

def get_meds(session, url_tup, end_date):
    med_url = url_tup[0]
    ref_url = url_tup[1]
        

    _ = session.get(ref_url)
    med_page = session.get(med_url).content.decode("utf-8")
    med_parser = BeautifulSoup(med_page, "html.parser")

    dose_date_ele = med_parser.find("th").text
    dose_date_ele = dose_date_ele.replace(',','').split(' ')
    time_of_day = dose_date_ele[0]
    med_date_mo = dose_date_ele[-3]
    mo_num = [idx for idx, item in enumerate(month_name) if item == med_date_mo][0]
    dose_datetime = datetime(int(dose_date_ele[-1]), mo_num, int(dose_date_ele[-2]) )
    dose_date = dose_datetime.strftime("%m/%d/%Y, %H:%M:%S")
    med_elements = med_parser.find_all("td")
    
    if med_elements == [] or (dose_datetime > end_date): #occasionally historical dates will return todays data, so we need to filter these out
        # med_objs = [Medication('None', 'None', 'None', '')]
        # dose_objs = [Dose(0, 0, dose_date, '', False, False, False, 'None')]
        med_objs = []
        dose_objs = []
    else:
        med_objs, dose_objs = process_daily_meds(med_elements, dose_date)
        for dose_obj in dose_objs:
            dose_obj.date = dose_date
            dose_obj.time_of_day = time_of_day 
            dose_obj.url = med_url
    
    return med_objs, dose_objs 

def clean(arr_in: list):
    # log.debug(f'in clean {arr_in}')
    if type(arr_in[0]) == str: 
        arr_out =[item.lower().replace('-',' ').replace(',','').strip() for item in arr_in]
    else:
        arr_out = arr_in
    # log.debug(f'out clean {arr_out}')
    return arr_out

def process_tags(med_elements)-> tuple[list[str], dict]:
    num_elements = len(med_elements)
    tag_phrases = [
        'intrapleural syringe'
         ,'ivpb'
         ,'omnicell override pull'
        ]
    indicators = [[None]]*len(tag_phrases)

    return_elements= [None]*num_elements
    for idx, phrase in enumerate(tag_phrases):
        indicators[idx]=[False]*num_elements
        for idy, element in enumerate(med_elements):
            if phrase.lower() in element.lower():
                indicators[idx][idy] = True
            
            element = element.replace(phrase,'')
            return_elements[idy] = element
    
    return clean(return_elements), indicators[0], indicators[1], indicators[2]


def process_daily_meds(med_elements, date):
    # removing html_tags, replacing unicode spaces
    tags_removed= [str(s).replace('<td>','').replace('</td>','').lower() for s in  med_elements]
    raw = tags_removed

    unicode_removed = [str(s).replace(f'\xa0',' ').replace(' %','%') for s in  tags_removed]
    log.debug(f'unicode_removed: {unicode_removed}')
    #splitting out time (if applicable)
    split = [s.split('-', maxsplit=1) if ':' in s else ('', s ) for s in unicode_removed]
    # log.info(f'split: {split}')

    try:
        time, med_dose_tag = zip(*split)
        log.info(f'split med_dose_tag: {med_dose_tag}')
    except ValueError as e:
        log.warning(f'No dates found on current url : {e}')
        time = [None for _ in unicode_removed]
        med_dose_tag = unicode_removed
        log.info(f'unsplit med_dose_tag: {med_dose_tag}')
    try:
        #removing tags appearing at the end of the medication string
        med_dose, ips, ivpb, override = process_tags(med_dose_tag)
        #splitting out medication names. Brand name is in parentehsis if it exists
        closing_paren_idx = [(re.search(r'\(',s),re.search(r'\)',s)) for s in med_dose]
        paren_bounds = [(openp.span()[0],closep.span()[1]) if openp else (0,0) for openp,closep in closing_paren_idx]
        name_split = [(s[:i[0]],s[i[0]+1:i[1]-1],s[i[1]:]) for s,i in zip(med_dose, paren_bounds)]
        gname, bname, remainder = list(zip(*name_split))
        log.info(f'name_split: {name_split}')

        #splitting out the dosage and units
        number_locations = [[(m.start(),m.end()) for m 
                                in re.finditer(r'(\d)+([,.]\d+)?',med)] for med in remainder] 
        log.info(f'remainder: {remainder}')
        log.info(f'number_locations: {number_locations}')
        first_num_to_last = [(group[0][0],group[-1][0],group[-1][1]) if len(group) >0 else (0,-1,-1) for group in number_locations] 
        mod_dose_split = [(split_list[:i[0]], split_list[i[0]:i[1]], split_list[i[1]:i[2]], split_list[i[2]:]) for split_list, i in zip(remainder, first_num_to_last)]

        #log.info(f'mod_dose_split: {mod_dose_split}')

        #splitting out the modality, dosage, and units
        mod1, mod2, qty, units = list(zip(*mod_dose_split))
        mod = [mod1 if mod1 else mod2 for mod1,mod2 in zip(mod1,mod2)]
        
        #resolving the remaining variables
        dates = [date for _ in unicode_removed]
        
        #create medication and dose objects
        to_med = [clean(arr) for arr in [gname, bname, mod, raw]]
        med_objs = [Medication(*row) for row in zip(*to_med)]

        to_dose = [clean(arr) for arr in [qty, units, dates, time, ips, ivpb, override, bname]]

        dose_objs = [Dose(*row) for row in zip(*to_dose)]
    except Exception as err:
        log.error(f'Error in process_daily_meds: {err}')
        breakpoint()
    # log.info(f'med_objs: {med_objs}')
    # log.info(f'dose_objs: {dose_objs}')
    return med_objs, dose_objs




def get_data(start_date:str, end_date:str = None):  
    today = datetime.now()
    code_on_ref_date = 66881
    code_ref_date = datetime(2024,2,11)
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    if start_date>today:
        start_date = today
    if end_date>today or end_date is None:
        end_date = today    

    start_date_code = (start_date - code_ref_date).days + code_on_ref_date
    end_date_code =  (end_date - code_ref_date).days + code_on_ref_date

    date_codes =  list(itertools.chain(range(start_date_code, end_date_code)))

    if start_date == today or end_date == today:
        #
        date_codes.append('') 

    with requests.session() as auth_session: 
        req = auth_session.get(URL).text 
        html = BeautifulSoup(req,"html.parser") 
        token = html.find("input", {"name": "__RequestVerificationToken"}).attrs["value"] 
        payload = { "__RequestVerificationToken": token, "DeviceId": Device_id, "postLoginUrl": "", "LoginInfo": login_info}
        req = auth_session.post(post_url,data=payload)
        if req.status_code != 200:  
            log.error('Login failed')
            exit()
        else:
            log.info('Login successful')
            med_list = []
            dose_list = []
            urls = build_glance_urls( date_codes = date_codes)
            for url_tup in urls:
                med_objs, dose_objs = get_meds(auth_session, url_tup, end_date)
                if len(med_objs)!=0:
                    med_list.extend(med_objs)
                if len(dose_objs)!=0:
                    dose_list.extend(dose_objs)
                

        auth_session.close()
        return med_list, dose_list


if __name__ == "__main__":
    med_list, dose_list = get_data(start_date='2024-02-13', end_date='2024-02-14')
    for idx, med in enumerate(med_list):
        if f'd5 % 0.45 % sodium chloride infusion' in med.raw:
            med_list[idx] = Medication('sodium chloride', '', 'infusion', f'd5 % 0.45 % sodium chloride infusion')
        if f'sodium chloride 0.9 % infusion' in med.raw:
            med_list[idx] = Medication('sodium chloride', '', 'infusion', f'sodium chloride 0.9 % infusion')
        if f'water flush' in med.raw:
            med_list[idx] = Medication('bottled water', '', 'flush', f'ottled water flush 200 ml')

    for idx, dose in enumerate(dose_list): 
        if dose.dosed_medication in ( f'5% 0.45% sodium chloride infusio', f'odium chloride 0.9% infusio'):
            dose.unit = f'%'
            dose.dosed_medication = f'sodium chloride'
        if 'bottled water' in dose.dosed_medication:
            dose.dosed_medication = f'bottled water'
            
    joined_list = [Joined(med,dose) for med, dose in zip(med_list, dose_list)] 
    med_data_range = "MedData!A:F"
    dose_data_range = "DoseData!A:F"
    join_data_range = "Joined!A:F"
    gsheets_export(med_list,med_data_range)
    gsheets_export(dose_list,dose_data_range)
    gsheets_export(joined_list,join_data_range)
