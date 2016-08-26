from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, sys
import pandas as pd
from multiprocessing import Process, Queue
import logging, re

logging.basicConfig(
    filename='wipp.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

num_threads = 1  # number of parallel threads
debug = True
minDelay = 3  # minimum delay between get requests 
maxDelay = 7  # maximum delay between get requests 
##url = 'https://wipp.edmundsassoc.com/Wipp1205/'

code_dict = {}
df = pd.read_csv('cntycode.csv')
input_data_df = pd.read_csv('input.csv')
urls = list(input_data_df['url'])

for i, row in df.iterrows():
    code = str(row[0]).strip()
    municipality = str(row[1]).strip()
    county = str(row[2]).strip()
    code_dict[code] = {'municipality':municipality, 'county':county}
    

def getElement(name):
    for td in tds:
        try:
            if name == 'Owner Name/Address:': 
                if td.getText().strip() == 'Owner Name/Address:':
                    return td.findNextSibling().getText().strip() + '\n' +\
                       td.findNext('tr').findAll('td')[1].getText().strip() + '\n' +\
                       td.findNext('tr').findNext('tr').findAll('td')[1].getText().strip()
            if td.getText().strip() == name:
                return td.findNextSibling().getText().strip()
            if name == 'Last Payment:':
                if 'Last Payment:' in td.getText() and td['class'][0] == 'valueColumn':
                    return td.getText().replace('Last Payment:','').strip()
                    break
        except Exception,e:
            pass

def getElements(name):
    data = []
    for td in tds:
        try:
            if td.getText().strip() == name:
                data.append([td.findNextSibling().getText().strip()])
        except Exception,e:
            pass

    return data

def split(a, n):
    """Function to split data evenly among threads"""
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]
            for i in xrange(n))

def scrapeData(driver, code_dict, url):    
    current_url = driver.current_url
    soup = BeautifulSoup(driver.page_source)
    print 'current_url', current_url
    tds = soup.findAll('td')

    returnData = {}

    Code = url.split('/')[-2]
    Code = re.findall('\d+', Code)[0]
    try:
        Municipality = code_dict[Code]['municipality']
    except:
        Municipality = ''
    try:
        County = code_dict[Code]['county']
    except:
        County = ''

    Link = url
    Current_Link =  driver.current_url
    try:
        Block = getElement('Block/Lot/Qual:').split()[0]
    except:
        Block = ''
    try:
        Lot = getElement('Block/Lot/Qual:').split()[1]
    except:
        Lot = ''
    try:
        Qual = getElement('Block/Lot/Qual:').split()[2]
    except:
        Qual = ''
    try:
        Property_Location = getElement('Property Location:')
    except:
        Property_Location =''
    try:
        Owner_Name = getElement('Owner Name/Address:').split('\n')[0]
    except:
        Owner_Name = ''
    try:
        Address = getElement('Owner Name/Address:').split('\n')[1]  + getElement('Owner Name/Address:').split('\n')[2]
    except:
        Address = ''
    try:
        Tax_Account_ID  = getElement('Tax Account Id:')
    except:
        Tax_Account_ID = ''
    try:
        Property_Class = getElement('Property Class:')
    except:
        Property_Class = ''
    try:
        Land_Value = getElement('Land Value:')
    except:
        Land_Value = ''
    try:
        Improvement_Value = getElement('Improvement Value:')
    except:
        Improvement_Value = ''
    try:
        Exempt_Value = getElement('Exempt Value:')
    except:
        Exempt_Value = ''
    try:
        Total_Assessed_Value = getElement('Total Assessed Value:')
    except:
        Total_Assessed_Value = ''
    try:
        Additional_Lots = getElement('Additional Lots:')
    except:
        Additional_Lots  = ''
    try:
        Deductions = getElement('Deductions:')
    except:
        Deductions = ''
    try:
        Special_Taxing_Districts = getElement('Special Taxing Districts:')
    except:
        Special_Taxing_Districts = ''
    try:
        Last_Payment = getElement('Last Payment:')
    except:
        Last_Payment = ''
    try:
        gwt_Label = driver.find_elements_by_class_name('gwt-Label')
        if gwt_Label[-1].text == 'Liens':
            gwt_Label[2].click()
    except:
        pass
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source)
    current_url = driver.current_url
    tds = soup.findAll('td')

    try:
        Certificate_Numbers = getElements('Certificate Number:')
    except:
        Certificate_Numbers = ''
    try:
        Subsequent_Charges = getElements('Subsequent Charges:')
    except:
        Subsequent_Charges = ''
    try:
        Sale_Amounts = getElements('Sale Amount:')
    except:
        Sale_Amounts = ''
    try:
        Sale_Dates = getElements('Sale Date:')
    except:
        Sale_Dates = ''
    try:
        Charge_Types = getElements('Charge Types:')
    except:
        Charge_Types = ''
    try:
        Lien_Holders = getElements('Lien Holder:')
    except:
        Lien_Holders = ''
    try:
        Year_in_Sales = getElements('Year in Sale:')
    except:
        Year_in_Sales = ''
    try:
        total_subsequent_charges = sum([float(g[0].replace(',','')) for g in getElements('Subsequent Charges:')])
    except:
        total_subsequent_charges = ''
    try:
        total_sale_amount = sum([float(g[0].replace(',','')) for g in getElements('Sale Amount:')])
    except:
        total_sale_amount = ''
    if total_sale_amount!='' and total_subsequent_charges!='':
        Total_Amount_owed_in_Liens = total_subsequent_charges + total_sale_amount
    elif  total_sale_amount=='' and total_subsequent_charges!='':
        Total_Amount_owed_in_Liens = total_subsequent_charges
    elif  total_sale_amount!='' and total_subsequent_charges=='':
        Total_Amount_owed_in_Liens = total_sale_amount
    else:
        Total_Amount_owed_in_Liens = ''

    for i in range(len(Certificate_Numbers)):
        returnData['Certificate_Number_' + str(i)] = Certificate_Numbers[i][0]
    for i in range(len(Subsequent_Charges)):
        returnData['Subsequent_Charge_' + str(i)] = Subsequent_Charges[i][0]
    for i in range(len(Sale_Amounts)):
        returnData['Sale_Amount_' + str(i)] = Sale_Amounts[i][0]
    for i in range(len(Sale_Dates)):
        returnData['Sale_Date_' + str(i)] = Sale_Dates[i][0]
    for i in range(len(Charge_Types)):
        returnData['Charge_Type_' + str(i)] = Charge_Types[i][0]
    for i in range(len(Lien_Holders)):
        returnData['Lien_Holder_' + str(i)] = Lien_Holders[i][0]
    for i in range(len(Year_in_Sales)):
        returnData['Year_in_Sale_' + str(i)] = Year_in_Sales[i][0]

    returnData['Code']=Code
    returnData['Municipality']=Municipality
    returnData['County']=County
    returnData['Link']=Link
    returnData['Block']=Block
    returnData['Lot']=Lot
    returnData['Qual']=Qual
    returnData['Property_Location']=Property_Location
    returnData['Owner_Name']=Owner_Name
    returnData['Address']=Address
    returnData['Tax_Account_ID']=Tax_Account_ID
    returnData['Property_Class']=Property_Class
    returnData['Land_Value']=Land_Value
    returnData['Improvement_Value']=Improvement_Value
    returnData['Exempt_Value']=Exempt_Value
    returnData['Total_Assessed_Value']=Total_Assessed_Value
    returnData['Additional_Lots']=Additional_Lots
    returnData['Deductions']=Deductions
    returnData['Total_Amount_owed_in_Liens']=Total_Amount_owed_in_Liens

    cols = ['Additional_Lots', 'Address', 'Block', 'Certificate_Number_1', 'Certificate_Number_2', 'Certificate_Number_3', 'Certificate_Number_4', 'Charge_Type_1', 'Charge_Type_2', 'Charge_Type_3', 'Charge_Type_4', 'Code', 'County', 'Deductions', 'Exempt_Value', 'Improvement_Value', 'Land_Value', 'Lien_Holder_1', 'Lien_Holder_2', 'Lien_Holder_3', 'Lien_Holder_4', 'Link', 'Lot', 'Municipality', 'Owner_Name', 'Property_Class', 'Property_Location', 'Qual', 'Sale_Amount_1', 'Sale_Amount_2', 'Sale_Amount_3', 'Sale_Amount_4', 'Sale_Date_1', 'Sale_Date_2', 'Sale_Date_3', 'Sale_Date_4', 'Subsequent_Charge_1', 'Subsequent_Charge_2', 'Subsequent_Charge_3', 'Subsequent_Charge_4', 'Tax_Account_ID', 'Total_Amount_owed_in_Liens', 'Total_Assessed_Value', 'Year_in_Sale_1', 'Year_in_Sale_2', 'Year_in_Sale_3', 'Year_in_Sale_4']

    for key in cols:
        if key not in returnData.keys():
            returnData[key] = ''

    return returnData
count = 0
driver = webdriver.Firefox()
for url in urls:
    print 'url', url
    labelData = ['a', 'ad']
    
    df1 = pd.DataFrame(columns = ['Additional_Lots', 'Address', 'Block', 'Certificate_Number_1', 'Certificate_Number_2', 'Certificate_Number_3', 'Certificate_Number_4', 'Charge_Type_1', 'Charge_Type_2', 'Charge_Type_3', 'Charge_Type_4', 'Code', 'County', 'Deductions', 'Exempt_Value', 'Improvement_Value', 'Land_Value', 'Lien_Holder_1', 'Lien_Holder_2', 'Lien_Holder_3', 'Lien_Holder_4', 'Link', 'Lot', 'Municipality', 'Owner_Name', 'Property_Class', 'Property_Location', 'Qual', 'Sale_Amount_1', 'Sale_Amount_2', 'Sale_Amount_3', 'Sale_Amount_4', 'Sale_Date_1', 'Sale_Date_2', 'Sale_Date_3', 'Sale_Date_4', 'Subsequent_Charge_1', 'Subsequent_Charge_2', 'Subsequent_Charge_3', 'Subsequent_Charge_4', 'Tax_Account_ID', 'Total_Amount_owed_in_Liens', 'Total_Assessed_Value', 'Year_in_Sale_1', 'Year_in_Sale_2', 'Year_in_Sale_3', 'Year_in_Sale_4'])
    while True:
        driver.get(url)

        element = WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.CLASS_NAME, "gwt-Button")) )
        element.click()
        time.sleep(2)
        labels  = driver.find_elements_by_tag_name('label')
##        if labels[count].text.strip() in labelData:
##            break
##        else:
##            labelData.append(labels[count].text.strip())
        
        element = WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.NAME, "picklistGroup")) )
        picklistGroup = driver.find_elements_by_name('picklistGroup')
        picklistGroup[count].click()
        time.sleep(5)
        element = WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.TAG_NAME, "td")) )
        #abc = scrapeData(driver, code_dict, url)
        current_url = driver.current_url
        while True:
            soup = BeautifulSoup(driver.page_source)
            print 'current_url', current_url
            tds = soup.findAll('td')
            if len(tds)>0:
                break

        returnData = {}

        Code = url.split('/')[-2]
        Code = re.findall('\d+', Code)[0]
        try:
            Municipality = code_dict[Code]['municipality']
        except:
            Municipality = ''
        try:
            County = code_dict[Code]['county']
        except:
            County = ''

        Link = url
        Current_Link =  driver.current_url
        try:
            Block = getElement('Block/Lot/Qual:').split()[0]
        except:
            Block = ''
        try:
            Lot = getElement('Block/Lot/Qual:').split()[1]
        except:
            Lot = ''
        try:
            Qual = getElement('Block/Lot/Qual:').split()[2]
        except:
            Qual = ''
        try:
            Property_Location = getElement('Property Location:')
        except:
            Property_Location =''
        try:
            Owner_Name = getElement('Owner Name/Address:').split('\n')[0]
        except:
            Owner_Name = ''
        try:
            Address = getElement('Owner Name/Address:').split('\n')[1]  + getElement('Owner Name/Address:').split('\n')[2]
        except:
            Address = ''
        try:
            Tax_Account_ID  = getElement('Tax Account Id:')
        except:
            Tax_Account_ID = ''
        try:
            Property_Class = getElement('Property Class:')
        except:
            Property_Class = ''
        try:
            Land_Value = getElement('Land Value:')
        except:
            Land_Value = ''
        try:
            Improvement_Value = getElement('Improvement Value:')
        except:
            Improvement_Value = ''
        try:
            Exempt_Value = getElement('Exempt Value:')
        except:
            Exempt_Value = ''
        try:
            Total_Assessed_Value = getElement('Total Assessed Value:')
        except:
            Total_Assessed_Value = ''
        try:
            Additional_Lots = getElement('Additional Lots:')
        except:
            Additional_Lots  = ''
        try:
            Deductions = getElement('Deductions:')
        except:
            Deductions = ''
        try:
            Special_Taxing_Districts = getElement('Special Taxing Districts:')
        except:
            Special_Taxing_Districts = ''
        try:
            Last_Payment = getElement('Last Payment:')
        except:
            Last_Payment = ''
        try:
            gwt_Label = driver.find_elements_by_class_name('gwt-Label')
            if gwt_Label[-1].text == 'Liens':
                gwt_Label[2].click()
        except:
            pass
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source)
        current_url = driver.current_url
        tds = soup.findAll('td')

        try:
            Certificate_Numbers = getElements('Certificate Number:')
        except:
            Certificate_Numbers = ''
        try:
            Subsequent_Charges = getElements('Subsequent Charges:')
        except:
            Subsequent_Charges = ''
        try:
            Sale_Amounts = getElements('Sale Amount:')
        except:
            Sale_Amounts = ''
        try:
            Sale_Dates = getElements('Sale Date:')
        except:
            Sale_Dates = ''
        try:
            Charge_Types = getElements('Charge Types:')
        except:
            Charge_Types = ''
        try:
            Lien_Holders = getElements('Lien Holder:')
        except:
            Lien_Holders = ''
        try:
            Year_in_Sales = getElements('Year in Sale:')
        except:
            Year_in_Sales = ''
        try:
            total_subsequent_charges = sum([float(g[0].replace(',','')) for g in getElements('Subsequent Charges:')])
        except:
            total_subsequent_charges = ''
        try:
            total_sale_amount = sum([float(g[0].replace(',','')) for g in getElements('Sale Amount:')])
        except:
            total_sale_amount = ''
        if total_sale_amount!='' and total_subsequent_charges!='':
            Total_Amount_owed_in_Liens = total_subsequent_charges + total_sale_amount
        elif  total_sale_amount=='' and total_subsequent_charges!='':
            Total_Amount_owed_in_Liens = total_subsequent_charges
        elif  total_sale_amount!='' and total_subsequent_charges=='':
            Total_Amount_owed_in_Liens = total_sale_amount
        else:
            Total_Amount_owed_in_Liens = ''

        for i in range(len(Certificate_Numbers)):
            returnData['Certificate_Number_' + str(i)] = Certificate_Numbers[i][0]
        for i in range(len(Subsequent_Charges)):
            returnData['Subsequent_Charge_' + str(i)] = Subsequent_Charges[i][0]
        for i in range(len(Sale_Amounts)):
            returnData['Sale_Amount_' + str(i)] = Sale_Amounts[i][0]
        for i in range(len(Sale_Dates)):
            returnData['Sale_Date_' + str(i)] = Sale_Dates[i][0]
        for i in range(len(Charge_Types)):
            returnData['Charge_Type_' + str(i)] = Charge_Types[i][0]
        for i in range(len(Lien_Holders)):
            returnData['Lien_Holder_' + str(i)] = Lien_Holders[i][0]
        for i in range(len(Year_in_Sales)):
            returnData['Year_in_Sale_' + str(i)] = Year_in_Sales[i][0]

        returnData['Code']=Code
        returnData['Municipality']=Municipality
        returnData['County']=County
        returnData['Link']=Link
        returnData['Block']=Block
        returnData['Lot']=Lot
        returnData['Qual']=Qual
        returnData['Property_Location']=Property_Location
        returnData['Owner_Name']=Owner_Name
        returnData['Address']=Address
        returnData['Tax_Account_ID']=Tax_Account_ID
        returnData['Property_Class']=Property_Class
        returnData['Land_Value']=Land_Value
        returnData['Improvement_Value']=Improvement_Value
        returnData['Exempt_Value']=Exempt_Value
        returnData['Total_Assessed_Value']=Total_Assessed_Value
        returnData['Additional_Lots']=Additional_Lots
        returnData['Deductions']=Deductions
        returnData['Total_Amount_owed_in_Liens']=Total_Amount_owed_in_Liens

        cols = ['Additional_Lots', 'Address', 'Block', 'Certificate_Number_1', 'Certificate_Number_2', 'Certificate_Number_3', 'Certificate_Number_4', 'Charge_Type_1', 'Charge_Type_2', 'Charge_Type_3', 'Charge_Type_4', 'Code', 'County', 'Deductions', 'Exempt_Value', 'Improvement_Value', 'Land_Value', 'Lien_Holder_1', 'Lien_Holder_2', 'Lien_Holder_3', 'Lien_Holder_4', 'Link', 'Lot', 'Municipality', 'Owner_Name', 'Property_Class', 'Property_Location', 'Qual', 'Sale_Amount_1', 'Sale_Amount_2', 'Sale_Amount_3', 'Sale_Amount_4', 'Sale_Date_1', 'Sale_Date_2', 'Sale_Date_3', 'Sale_Date_4', 'Subsequent_Charge_1', 'Subsequent_Charge_2', 'Subsequent_Charge_3', 'Subsequent_Charge_4', 'Tax_Account_ID', 'Total_Amount_owed_in_Liens', 'Total_Assessed_Value', 'Year_in_Sale_1', 'Year_in_Sale_2', 'Year_in_Sale_3', 'Year_in_Sale_4']

        for key in cols:
            if key not in returnData.keys():
                returnData[key] = ''
        #print returnData
        dd = pd.DataFrame([returnData])
        df1 = pd.concat([df1, dd], axis=0)
        print df1.shape
        count+=1
        if count %3==0:
            labelData = []
        if count%19==0:
            buttons = driver.find_elements_by_css_selector('.gwt-Button')
            for button in buttons:
                try:
                    if button.text.strip() == 'Next 20':
                        button.click()
                except:
                    pass

        time.sleep(2)
driver.close()

