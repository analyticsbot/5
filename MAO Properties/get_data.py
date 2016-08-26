from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
url = 'https://wipp.edmundsassoc.com/Wipp0103/'

driver = webdriver.Firefox()

driver.get(url)
soup = BeautifulSoup(driver.page_source)
element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS, "gwt-Button"))
    )
element.click()
driver.find_element_by_name('picklistGroup').click()

cur_url = driver.current_url
tds = soup.findAll('td')

def getElement(name):
    for td in tds:
        try:
            if td.text.strip() == name:
                return td.findNextSibling('td').text
        except:
            pass

block = getElement('Block/Lot/Qual:').split()[0]
lot = getElement('Block/Lot/Qual:').split()[1]
qual = getElement('Block/Lot/Qual:').split()[2]
code = url.split('/')[-2]
Municipality = ''
Link = url
Property_Location = getElement('Property Location:')
Owner_Name = 
Address = 
Tax_Account_ID = getElement('Tax Account Id:')
Property_Class = getElement('Property Class:')
Land_Value = getElement('Land Value:')
Improvement_Value = getElement('Improvement Value:')
Exempt_Value = getElement('Exempt Value:')
Total_Assessed_Value = getElement('Total Assessed Value:')
Additional_Lots = getElement('Additional Lots:')
Deductions = getElement('Deductions:') 
Total_Amount_owed_in_Liens_Sum_of_all_Sale_Amounts+Subsequent_Charges_Fields = 
Certificate_Number = 
Subsequent_Charges = 
Sale_Amount = 
Sale_Date = 
Charge_Types = 
Lien_Holder  = 
Year_in_Sale = 
Certificate_Number = 
Sale_Amount = 
Subsequent_Charges = 
Sale_Date = 
Charge_Types = 
Lien_Holder = 
Year_in_Sale = 
Certificate_Number = 
Sale_Amount = 
Subsequent_Charges = 
Sale_Date = 
Charge_Types = 
Lien_Holder = 
Year_in_Sale = 
