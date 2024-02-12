import requests
import itertools
from datetime import datetime, time
from calendar import month_name

import re
import logging
from dataclasses import dataclass

from gsheets import gsheets_export

#medicine for morning (1), afternoon (2), ...
#https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=1&cat=999&dat=
#https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=2&cat=999&dat=

# Day at a glace 
#https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&sch=66879




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
        for name in med_dict.keys():
            if name.lower() in self.name.lower():
                self.name = med_dict[name][0]
                self.modality = med_dict[name][1]
                self.dosage = med_dict[name][2]
                self.dosage_unit = med_dict[name][3]
            else:
                pass
        return self

@dataclass
class Dose:
    # medicine_id: str
    quantity: str
    unit: str
    date: datetime
    dose_time: time = None
    ips: bool = False
    ivpb: bool = False
    omnicell_override_pull: bool = False
    dosed_medication: Medication = None

@dataclass
class Treatment:
    frequency: str
    start_date: str
    end_date: str
    instructions: str
    side_effects: str


login_info = {"Type":"StandardLogin","Credentials":{"Username":"Q3dpc2NobWV5","Password":"TXlDaGFydHB3MzMh"}}
Device_id = "WEB,276a0198b48a4741b8d6b2605db47678,1QeY2eV4+nFGmxvY5KaPAkBfr5BA/NN6H9Kdku6KeZM="
login_info = '{"Type":"StandardLogin","Credentials":{"Username":"Q3dpc2NobWV5ZQ==","Password":"TXlDaGFydHB3MzMh"}}'
medication_url = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&sch=66878'
itinerary_url = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary'

given_Day_meds = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=1&cat=999&dat=66878'

#  funky_meds = {
#         'Cellcept': ('mycophenolate (Cellcept)', '200mg/ml suspension', '500', 'mg'),
#         'Duo-Neb':  ('ipratropium-albuterol (Duo-Neb)', '0.5mg-3mg/3ml solution', '3', 'ml'),
#         'AndroGel': ('testosterone (AndroGel)', '50mg/5 gram (1 %) gel', '50', 'mg'),
#         'Lidoderm': ('lidocaine (Lidoderm)', '5% patch', '1', 'patch')
#           Medication(name='', modality='sodium chloride', dosage='0.9',
#            dosage_unit='% infusion  - Omnicell Override Pull', time=None)]
#         }


def clean(arr_in: list):
    if type(arr_in[0]) == str: 
        arr_out =[item.lower().replace('-','').strip() for item in arr_in]
    else:
        arr_out = arr_in
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
    
    return clean(return_elements), tag_phrases[0], tag_phrases[1], tag_phrases[2]


def process_daily_meds(med_elements):
    # removing html_tags, replacing unicode spaces
    unicode_removed = [str(s).replace(f'\xa0',' ').replace('<td>','').replace('</td>','') for s in  med_elements]
    
    #splitting out time (if applicable)
    split = [s.split(' - ', maxsplit=1) for s in unicode_removed]
    # log.info(f'split: {split}')

    try:
        time, med_dose_tag = zip(*split)
    except ValueError as e:
        log.warning(f'No dates found on current url : {e}')
        time = [None for _ in unicode_removed]
        med_dose_tag = unicode_removed
        log.info(f'unsplit med_dose_tag: {med_dose_tag}')
    
    #removing tags appearing at the end of the medication string
    med_dose, ips, ivpb, override = process_tags(med_dose_tag)
    #splitting out medication names. Brand name is in parentehsis if it exists
    closing_paren_idx = [(re.search(r'\(',s),re.search(r'\)',s)) for s in med_dose]
    paren_bounds = [(openp.span()[0],closep.span()[1]) if openp else (0,0) for openp,closep in closing_paren_idx]
    name_split = [(s[:i[0]],s[i[0]+1:i[1]-1],s[i[1]:]) for s,i in zip(med_dose, paren_bounds)]
    gname, bname, remainder = list(zip(*name_split))
    #log.info(f'name_split: {name_split}')

    #splitting out the dosage and units
    number_locations = [[(m.start(),m.end()) for m 
                            in re.finditer(r'(\d)+([,.]\d+)?',med)] for med in remainder] 
    first_num_to_last = [(group[0][0],group[-1][0],group[-1][1]) for group in number_locations] 
    mod_dose_split = [(split_list[:i[0]], split_list[i[0]:i[1]], split_list[i[1]:i[2]], split_list[i[2]:]) for split_list, i in zip(remainder, first_num_to_last)]

    #log.info(f'mod_dose_split: {mod_dose_split}')

    #splitting out the modality, dosage, and units
    mod1, mod2, qty, units = list(zip(*mod_dose_split))
    mod = [mod1 if mod1 else mod2 for mod1,mod2 in zip(mod1,mod2)]
    
    #resolving the remaining variables
    date = [datetime.now() for _ in unicode_removed]
    raw = unicode_removed

    #create medication and dose objects
    to_med = [clean(arr) for arr in [gname, bname, mod, raw]]
    med_objs = [Medication(*row) for row in zip(*to_med)]

    to_dose = [clean(arr) for arr in [qty, units, date, time, ips, ivpb, override]]
    dose_objs = [Dose(*row) for row in zip(*to_dose)]
    
    # log.info(f'med_objs: {med_objs}')
    # log.info(f'dose_objs: {dose_objs}')
    return med_objs, dose_objs

def configure_log():
    logger = logging.getLogger('main_logger')
    logger.setLevel(logging.DEBUG)

    ch = logging.FileHandler('scrapper.log', mode='w')  
    ch.setLevel(logging.DEBUG)

    st = logging.StreamHandler()  
    st.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    st.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    logger.addHandler(st)
    return logger

def build_glance_urls(cat = '999', dats= [''], tods:list[str] = ['1','2','3','4'] ):
    urls = ['']*len(tods)*len(dats)
    for idx, tod in enumerate(tods):
        for idy, dat in enumerate(dats):
            url = f'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod={tod}&cat={cat}&dat={dat}'
            urls[idx*len(dats) + idy] = url
    return urls

def get_meds(session, url):
    med_page = session.get(given_Day_meds).content.decode("utf-8")
    med_parser = BeautifulSoup(med_page, "html.parser")

    dose_date_ele = med_parser.find("th").text
    dose_date_ele = dose_date_ele.replace(',','').split(' ')
    med_date_mo = dose_date_ele[-3]
    mo_num = [idx for idx, item in enumerate(month_name) if item == med_date_mo][0]
    dose_date = datetime(int(dose_date_ele[-1]), mo_num, int(dose_date_ele[-2]) )

    med_elements = med_parser.find_all("td")
    
    log.info(f'med_elements for {url}:  {med_elements}')
    
    med_objs, dose_objs = process_daily_meds(med_elements)

    for dose_obj in dose_objs:
        dose_obj.date = dose_date

    return med_objs, dose_objs 


def get_data(date):  

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
            urls = build_glance_urls()
            for url in urls:
                med_objs, dose_objs = get_meds(auth_session, url)
                med_list.extend(med_objs)
                dose_list.extend(dose_objs)

        auth_session.close()
        return med_list, dose_list

log= configure_log()

if __name__ == "__main(__":
    med_list, dose_list = get_data(datetime.now())
    gsheets_export(med_list)
    gsheets_export(dose_list)


# https://mychart.emoryhealthcare.org/MyChart-prd/Authentication/Login/DoLogin


# <input name="__RequestVerificationToken" 
# type="hidden" 
# value="OGvWMlwWIXHe8ONRHpH1UoSNGPoGDvl2KDytJCnogPo8_kvhQKwM-j4ZdhXl882x1ou3SiykuRyCpS65QhrqM2dphJ01" 
# autocomplete="off">

# <form class="hidden" 
# action="/MyChart-prd/Authentication/Login/DoLogin" 
# autocomplete="off" id="actualLogin" 
# method="post" target="_top">
# <input name="__RequestVerificationToken"
# type="hidden" 
# value="OGvWMlwWIXHe8ONRHpH1UoSNGPoGDvl2KDytJCnogPo8_kvhQKwM-j4ZdhXl882x1ou3SiykuRyCpS65QhrqM2dphJ01" autocomplete="off">
# <div class="formcontents">
# </div>
# <input type="hidden" name="DeviceId" 
# value="WEB,276a0198b48a4741b8d6b2605db47678,1QeY2eV4+nFGmxvY5KaPAkBfr5BA/NN6H9Kdku6KeZM=">
# <input type="hidden" name="postLoginUrl" value=""></form>"td"