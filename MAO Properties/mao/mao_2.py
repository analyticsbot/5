## import all necessary modules
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, sys
import pandas as pd
from multiprocessing import Process, Queue
import logging, re
from threading import Thread

logging.basicConfig(
    filename='wipp.log',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

num_threads = 1 # number of parallel threads
debug = True # whether to print updates on screen
minDelay = 3  # minimum delay between get requests 
maxDelay = 7  # maximum delay between get requests 
STOP_AFTER = 2 # stop after finding these many NO data pages. go to the next url in the list
CHECK_BREAK = 0 # this is for testing purposes. This will ensure that ONLY these many records per WIPP is outputed
column_names = ['Code', 'Property_Class', 'Improvement_Value', 'Municipality', 'Total_Amount_owed_in_Liens', 'Exempt_Value', \
                    'Land_Value', 'County', 'Qual', 'Deductions', 'Owner_Name', 'Link', 'Current_Link', 'Total_Assessed_Value', \
                    'Lot', 'Address', 'Additional_Lots', 'Property_Location', 'Tax_Account_ID', 'Block', 'Special_Taxing_Districts',\
                    'Last_Payment', 'Certificate_Number_1', 'Subsequent_Charge_1', 'Sale_Amount_1', 'Sale_Date_1', 'Charge_Type_1',\
                    'Lien_Holder_1', 'Year_in_Sale_1', 'Certificate_Number_2', 'Subsequent_Charge_2', 'Sale_Amount_2', 'Sale_Date_2',\
                    'Charge_Type_2', 'Year_in_Sale_2', 'Lien_Holder_2', 'Certificate_Number_3', 'Subsequent_Charge_3', 'Sale_Amount_3',\
                    'Sale_Date_3', 'Charge_Type_3', 'Lien_Holder_3', 'Year_in_Sale_3', 'Certificate_Number_4', 'Subsequent_Charge_4', \
                    'Sale_Amount_4', 'Sale_Date_4', 'Charge_Type_4', 'Lien_Holder_4', 'Year_in_Sale_4']

logging.info('Number of threads = ' + str(num_threads) + ' minDelay = ' + str(minDelay) + ' maxDelay  = ' + str(maxDelay) + \
             ' STOP_AFTER = ' + str(STOP_AFTER) + ' CHECK_BREAK = ' + str(CHECK_BREAK))
if debug:
    'Number of threads = ' + str(num_threads) + ' minDelay = ' + str(minDelay) + ' maxDelay  = ' + str(maxDelay) + \
             ' STOP_AFTER = ' + str(STOP_AFTER) + ' CHECK_BREAK = ' + str(CHECK_BREAK)
code_dict = {}
df = pd.read_csv('cntycode.csv')
input_data_df = pd.read_csv('input.csv')
urls = list(input_data_df['url'])

for i, row in df.iterrows():
    code = str(row[0]).strip()
    municipality = str(row[1]).strip()
    county = str(row[2]).strip()
    code_dict[code] = {'municipality':municipality, 'county':county}

if debug:
    print 'City Code, municipality, county data is loaded to a dictionary'
logging.info('City Code, municipality, county data is loaded to a dictionary')    

def getElement(tds, name):
    """Function to get specific elements from the top table on any taxpage
    tds = soup object of all the td tags present on the page
    name = name of the element that is to be extracted from the page
    """
    ## apart from owner/address and last payment, all other tags are easy
    ## just check the tag text, if it's name then the next value is the
    ## text we are looking for
    ## for owner name/address - we need to look at the next element
    ## and the next tr tag's td and one more
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

def getElements(tds, name):
    '''function to get elements from the liens page such as certificate numbers
    tds = soup objects of all td tags
    name = name of the element to be extracted
    '''
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

def getData(i, urls_1, debug, minDelay, maxDelay, code_dict, STOP_AFTER, CHECK_BREAK, column_names):
    ''' main function to scrape the data from each taxpage
    i = thread number
    urls_1 = list of urls for this particular thread
    debug = print updates to screen
    minDelay = minimum delay between each request
    maxDelay = max delay
    code_dict = dictionary for all code, municipality, county
    STOP_AFTER = stop after these many concurrent blank pages
    CHECK_BREAK = if 0, scrape all tax pages, if non zero scrape those many pages
    column_names = columns to scrape
    '''
    count1 = 1
    count=100000
    norecords = 0
    c = 0
    driver = webdriver.Firefox()
    if debug:
        print 'Started the selenium firefox browser for thread ## ', i
    logging.info('Started the selenium firefox browser for thread ## ' + str(i))
    df1 = pd.DataFrame(columns = column_names)

    for url in urls_1:
        Code1 = url.split('/')[-2]
        while True:
            url1 = url + '#taxPage'+str(count)
            print 'url1', url1
            try:
                alert = driver.switch_to_alert()
                alert.accept()
            except:
                pass
            driver.get(url1)
            time.sleep(2)
            count+=1
            count1+=1
            c+=1

            print 'norecords', norecords
            if norecords ==STOP_AFTER:
                count = 1
                norecords = 0
                df1 = pd.DataFrame(columns = column_names)
                if debug:
                    print 'Exiting loop since a break has been met. STOP_AFTER, ' + url1
                logging.info('Exiting loop since a break has been met. STOP_AFTER, ' + url1)
                break
            
            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present(),
                                               'Timed out waiting for PA creation ' +
                                               'confirmation popup to appear.')

                alert = driver.switch_to_alert()
                alert.accept()
                if debug:
                    print 'alert present. No data exists for taxpage', url1
                logging.info('alert present. No data exists for taxpage = ' + str( url1))
                norecords +=1
                if debug:
                    print 'No more records for url ' + str(url1)
                logging.info('No more records for url ' + str(url1))
                continue
            except:
                norecords = 0
                
            if CHECK_BREAK !=0:                
                if c>CHECK_BREAK:
                    c = 0
                    count = 1
                    norecords = 0
                    df1 = pd.DataFrame(columns = column_names)
                    if debug:
                        print 'Exiting the loop for url = ', url, ' since check break is met'
                    logging.info('Exiting the loop for url = '+str( url)  + ' since check break is met')
                    break
            
            current_url = driver.current_url
            
            while True:
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source)
                if debug:
                    print 'current_url', current_url
                logging.info('current_url = ' + current_url)
                tds = soup.findAll('td')
                if len(tds)>0 and 'Return to Home' in driver.page_source:
                    break
            ## intialize a dictionary to hold the objects
            returnData = {}

            ## try and parse all the data from the page

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
                Block = getElement(tds, 'Block/Lot/Qual:').split()[0]
            except Exception,e:
                Block = ''
                continue
            
            try:
                Lot = getElement(tds, 'Block/Lot/Qual:').split()[1]
            except:
                Lot = ''
            try:
                Qual = getElement(tds, 'Block/Lot/Qual:').split()[2]
            except:
                Qual = ''
            try:
                Property_Location = getElement(tds, 'Property Location:')
            except:
                Property_Location =''
            try:
                Owner_Name = getElement(tds, 'Owner Name/Address:').split('\n')[0]
            except:
                Owner_Name = ''
            try:
                Address = getElement(tds, 'Owner Name/Address:').split('\n')[1]  + ' ' + getElement(tds, 'Owner Name/Address:').split('\n')[2]
            except:
                Address = ''
            try:
                Tax_Account_ID  = getElement(tds, 'Tax Account Id:')
            except:
                Tax_Account_ID = ''
            try:
                Property_Class = getElement(tds, 'Property Class:')
            except:
                Property_Class = ''
            try:
                Land_Value = getElement(tds, 'Land Value:')
            except:
                Land_Value = ''
            try:
                Improvement_Value = getElement(tds, 'Improvement Value:')
            except:
                Improvement_Value = ''
            try:
                Exempt_Value = getElement(tds, 'Exempt Value:')
            except:
                Exempt_Value = ''
            try:
                Total_Assessed_Value = getElement(tds, 'Total Assessed Value:')
            except:
                Total_Assessed_Value = ''
            try:
                Additional_Lots = getElement(tds, 'Additional Lots:')
            except:
                Additional_Lots  = ''
            try:
                Deductions = getElement(tds, 'Deductions:')
            except:
                Deductions = ''
            try:
                Special_Taxing_Districts = getElement(tds, 'Special Taxing Districts:')
            except:
                Special_Taxing_Districts = ''
            try:
                Last_Payment = getElement(tds, 'Last Payment:')
            except:
                Last_Payment = ''
            try:
                gwt_Label = driver.find_elements_by_class_name('gwt-Label')
                for gwt in  gwt_Label:
                    if gwt.text == 'Liens':
                        gwt.click()
            except:
                pass
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source)
            current_url = driver.current_url
            tds = soup.findAll('td')

            try:
                Certificate_Numbers = getElements(tds, 'Certificate Number:')
            except:
                Certificate_Numbers = ''
            try:
                Subsequent_Charges = getElements(tds, 'Subsequent Charges:')
            except:
                Subsequent_Charges = ''
            try:
                Sale_Amounts = getElements(tds, 'Sale Amount:')
            except:
                Sale_Amounts = ''
            try:
                Sale_Dates = getElements(tds, 'Sale Date:')
            except:
                Sale_Dates = ''
            try:
                Charge_Types = getElements(tds, 'Charge Types:')
            except:
                Charge_Types = ''
            try:
                Lien_Holders = getElements(tds, 'Lien Holder:')
            except:
                Lien_Holders = ''
            try:
                Year_in_Sales = getElements(tds, 'Year in Sale:')
            except:
                Year_in_Sales = ''
            try:
                total_subsequent_charges = sum([float(g[0].replace(',','')) for g in getElements(tds, 'Subsequent Charges:')])
            except:
                total_subsequent_charges = ''
            try:
                total_sale_amount = sum([float(g[0].replace(',','')) for g in getElements(tds, 'Sale Amount:')])
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

            for i in range(1, len(Certificate_Numbers)+1):
                returnData['Certificate_Number_' + str(i)] = Certificate_Numbers[i-1][0]
            for i in range(1, len(Subsequent_Charges)+1):
                returnData['Subsequent_Charge_' + str(i)] = Subsequent_Charges[i-1][0]
            for i in range(1, len(Sale_Amounts)+1):
                returnData['Sale_Amount_' + str(i)] = Sale_Amounts[i-1][0]
            for i in range(1, len(Sale_Dates)+1):
                returnData['Sale_Date_' + str(i)] = Sale_Dates[i-1][0]
            for i in range(1, len(Charge_Types)+1):
                returnData['Charge_Type_' + str(i)] = Charge_Types[i-1][0]
            for i in range(1, len(Lien_Holders)+1):
                returnData['Lien_Holder_' + str(i)] = Lien_Holders[i-1][0]
            for i in range(1, len(Year_in_Sales)+1):
                returnData['Year_in_Sale_' + str(i)] = Year_in_Sales[i-1][0]

            returnData['Code']=Code
            returnData['Municipality']=Municipality
            returnData['County']=County
            returnData['Link']=Link
            returnData['Current_Link']=Current_Link
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
            returnData['Special_Taxing_Districts']=Special_Taxing_Districts
            returnData['Last_Payment']=Last_Payment
            returnData['Total_Amount_owed_in_Liens']=Total_Amount_owed_in_Liens

            for key in column_names:
                if key not in returnData.keys():
                    returnData[key] = ''

            dd = pd.DataFrame([returnData])
            df1 = pd.concat([df1, dd], axis=0)
        df2 = df1[column_names]
        if debug:
            print 'Outputting data to csv. Filename = ' + Code1 + '.csv'
        logging.info('Outputting data to csv. Filename = ' + Code1 + '.csv')
        df2.to_csv(Code1 + '.csv', index = False, encoding = 'utf-8')
    if debug:
        print 'Closing the webdriver'
    driver.close()

distributed_urls = list(split(list(urls), num_threads))
getData( 1,
                    distributed_urls[0],
                    debug,
                    minDelay,
                    maxDelay,
                    code_dict,
                    STOP_AFTER,
                    CHECK_BREAK, column_names)

if __name__ == "__main__":
    dataThreads = []
    for i in range(num_threads):
        data = distributed_urls[i]
        dataThreads.append(
            Process(
                target=getData,
                args=(
                    i + 1,
                    data,
                    debug,
                    minDelay,
                    maxDelay,
                    code_dict,
                    STOP_AFTER,
                    CHECK_BREAK,
                    column_names,

                )))
    j = 1
    for thread in dataThreads:
        sys.stdout.write('starting scraper ##' + str(j) + '\n')
        logging.info('starting scraper ##' + str(j) + '\n')
        j += 1
        thread.start()
    j = 1
    try:
        for worker in dataThreads:
            sys.stdout.write('stopping scraper ##' + str(j) + '\n')
            worker.join(10)
    except KeyboardInterrupt:
        print 'Received ctrl-c'
        logging.info('Received ctrl-c' + '\n' + '\n')
        for worker in dataThreads:
            worker.terminate()
            worker.join(10)



