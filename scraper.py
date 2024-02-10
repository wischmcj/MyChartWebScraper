import requests
# import numpy as np
#!pip install selenium
# from selenium import webdriver

from bs4 import BeautifulSoup 

URL = "https://mychart.emoryhealthcare.org/mychart-prd/Authentication/Login/" 
 
post_url  = "https://mychart.emoryhealthcare.org/MyChart-prd/Authentication/Login/DoLogin"
payload = { 
	"uname": "cwischmeye", 
	"pass": "" 
} 
#  __RequestVerificationToken=OGvWMlwWIXHe8ONRHpH1UoSNGPoGDvl2KDytJCnogPo8_kvhQKwM-j4ZdhXl882x1ou3SiykuRyCpS65QhrqM2dphJ01&DeviceId=WEB%2C276a0198b48a4741b8d6b2605db47678%2C1QeY2eV4%2BnFGmxvY5KaPAkBfr5BA%2FNN6H9Kdku6KeZM%3D&postLoginUrl=&LoginInfo=%7B%22Type%22%3A%22StandardLogin%22%2C%22Credentials%22%3A%7B%22Username%22%3A%22Q3dpc2NobWV5%22%2C%22Password%22%3A%22TXlDaGFydHB3MzMh%22%7D%7D
# __RequestVerificationToken=OGvWMlwWIXHe8ONRHpH1UoSNGPoGDvl2KDytJCnogPo8_kvhQKwM-j4ZdhXl882x1ou3SiykuRyCpS65QhrqM2dphJ01
# DeviceId=WEB,276a0198b48a4741b8d6b2605db47678,1QeY2eV4+nFGmxvY5KaPAkBfr5BA/NN6H9Kdku6KeZM=
# postLoginUrl

# HTTP/1.1 302 Found
# Cache-Control: no-cache, no-store, must-revalidate
# Pragma: no-cache
# Content-Type: text/html; charset=utf-8
# Expires: -1
# Location: /MyChart-prd/Authentication/Login?error=usernameloginfailed
# Content-Security-Policy-Report-Only: default-src 'self';base-uri 'self';frame-ancestors 'self';frame-src https://* 'self' epichttp:;script-src 'nonce-8102f7b055a8490ab9326cda5a2d8088' https://mychart.eushc.org 'self';img-src https://* 'self' blob: data:;style-src https://mychart.eushc.org 'self' 'unsafe-inline';form-action 'self';media-src https://* 'self';
# Pics-Label: (PICS-1.1 "http://www.icra.org/pics/vocabularyv03/" l on "2010.05.31T16:34-0400" exp "2100.12.31T12:00-0400" r (n 0 s 0 v 0 l 0 oa 0 ob 0 oc 0 od 0 oe 0 of 0 og 0 oh 0 c 0))
# X-Content-Type-Options: nosniff
# Strict-Transport-Security: max-age=31536000
# Date: Sat, 10 Feb 2024 16:17:36 GMT
# Content-Length: 176

login_info = {"Type":"StandardLogin","Credentials":{"Username":"Q3dpc2NobWV5","Password":"TXlDaGFydHB3MzMh"}}
Device_id = "WEB,276a0198b48a4741b8d6b2605db47678,1QeY2eV4+nFGmxvY5KaPAkBfr5BA/NN6H9Kdku6KeZM="
login_info = '{"Type":"StandardLogin","Credentials":{"Username":"Q3dpc2NobWV5ZQ==","Password":"TXlDaGFydHB3MzMh"}}'
medication_url = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&sch=66878'
itinerary_url = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary'

given_Day_meds = 'https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=1&cat=999&dat=66878'
with requests.session() as auth_session: 
    req = auth_session.get(URL).text 
    html = BeautifulSoup(req,"html.parser") 
    token = html.find("input", {"name": "__RequestVerificationToken"}).attrs["value"] 
    payload = { "__RequestVerificationToken": token, "DeviceId": Device_id, "postLoginUrl": "", "LoginInfo": login_info}
    req = auth_session.post(post_url,data=payload)
    r = auth_session.get(medication_url).content.decode()
    soup = BeautifulSoup (r, "html.parser") 
    med_page = auth_session.get(given_Day_meds).content.decode()
    med_parser = BeautifulSoup(med_page, "html.parser")
    med_elements =med_parser.find_all("td")

	# usernameDiv = soup.find("span", class_="p-nickname vcard-username d-block") 
    breakpoint()
    # html = BeautifulSoup(req,"html.parser")
    breakpoint()
    auth_session.close()
    html.find()


def prescription_list(row):     
    """ This function returns a list of all the prescription       
    medication an individual is prescribed"""    

    if row['Prescriptions'] is np.nan: 
        return(np.nan)
    else: 
        drugs = row['Prescriptions'].split(", ")
        
        drugs_list = []
        
        for i in drugs: 
                drugs_list.append(i)      
           
        return(drugs_list)       

def nhs_details(drug): 
    
    drug = drug.lower()
    try: 
        driver.get(f"https://www.nhs.uk/medicines/{drug}/")
        section_1 = driver.find_element_by_xpath(f"""//*[@id="about-{drug}"]/div""")
        section_1_text = section_1.text.replace("\n", " ")
        section_2 = driver.find_element_by_xpath("""//*[@id="key-facts"]/div""")
        section_2_text = section_2.text.replace("\n", " ")
        try: 
            section_3 = driver.find_element_by_xpath(f"""//*[@id="who-can-and-cannot-take-{drug}"]/div""")
            section_3_text = section_3.text.replace("\n", " ")
        except: 
            section_3 = driver.find_element_by_xpath(f"""//*[@id="who-can-and-cant-take-{drug}"]/div""")
            section_3_text = section_3.text.replace("\n", " ")
   
        return(section_1_text, section_2_text, section_3_text)
        
    except: 
        driver.get(f"https://www.nhs.uk/medicines/{drug}-for-adults/")
        section_1 = driver.find_element_by_xpath(f"""//*[@id="about-{drug}-for-adults"]/div""")
        section_1_text = section_1.text.replace("\n", " ")
        section_2 = driver.find_element_by_xpath("""//*[@id="key-facts"]/div""")
        section_2_text = section_2.text.replace("\n", " ")
        section_3 = driver.find_element_by_xpath(f"""//*[@id="who-can-and-cannot-take-{drug}"]/div""")
        section_3_text = section_3.text.replace("\n", " ")
   
    
        return(section_1_text, section_2_text, section_3_text)
 
    



# __RequestVerificationToken=OGvWMlwWIXHe8ONRHpH1UoSNGPoGDvl2KDytJCnogPo8_kvhQKwM-j4ZdhXl882x1ou3SiykuRyCpS65QhrqM2dphJ01&DeviceId=WEB%2C276a0198b48a4741b8d6b2605db47678%2C1QeY2eV4%2BnFGmxvY5KaPAkBfr5BA%2FNN6H9Kdku6KeZM%3D&postLoginUrl=&LoginInfo=%7B%22Type%22%3A%22StandardLogin%22%2C%22Credentials%22%3A%7B%22Username%22%3A%22Q3dpc2NobWV5%22%2C%22Password%22%3A%22TXlDaGFydHB3MzMh%22%7D%7D

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