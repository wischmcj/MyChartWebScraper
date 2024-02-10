import requests
import pandas as pd 
import numpy as np
#!pip install selenium
from selenium import webdriver


URL = "http://testphp.vulnweb.com/userinfo.php" 
 
payload = { 
	"uname": "cwischmeye", 
	"pass": "" 
} 
s = requests.session() 
response = s.post(URL, data=payload) 
print(response.status_code) # If the request went Ok we usually get a 200 status. 
 
from bs4 import BeautifulSoup 
soup = BeautifulSoup(response.content, "html.parser") 
protected_content = soup.find(attrs={"id": "pageName"}).text 
print(protected_content)

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
type="hidden" 
value="OGvWMlwWIXHe8ONRHpH1UoSNGPoGDvl2KDytJCnogPo8_kvhQKwM-j4ZdhXl882x1ou3SiykuRyCpS65QhrqM2dphJ01" 
autocomplete="off">

<form class="hidden" 
action="/MyChart-prd/Authentication/Login/DoLogin" 
autocomplete="off" id="actualLogin" 
method="post" target="_top">
<input name="__RequestVerificationToken"
type="hidden" 
value="OGvWMlwWIXHe8ONRHpH1UoSNGPoGDvl2KDytJCnogPo8_kvhQKwM-j4ZdhXl882x1ou3SiykuRyCpS65QhrqM2dphJ01" autocomplete="off">
<div class="formcontents">
</div>
<input type="hidden" name="DeviceId" 
value="WEB,276a0198b48a4741b8d6b2605db47678,1QeY2eV4+nFGmxvY5KaPAkBfr5BA/NN6H9Kdku6KeZM=">
<input type="hidden" name="postLoginUrl" value=""></form>