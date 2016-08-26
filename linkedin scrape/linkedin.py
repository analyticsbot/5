from selenium import webdriver
import sys, time
import pandas as pd

df = pd.DataFrame(columns = ['image', 'name', 'profile', 'desc', 'area'])

driver = webdriver.Firefox()

EMAIL = 'ivar.dodo12345@gmail.com'
PASSWORD = 'number1'

url = 'https://www.linkedin.com/vsearch/p?adv=true&trk=advsrch'

try:
    driver.get(url)
    print '[+] Opened the url in firefox'
except:
    print '[+] Some issue happened. Cant open firefox. Exiting'
    sys.exit(1)
time.sleep(5)
driver.find_element_by_class_name('sign-in-link').click()
time.sleep(15)
email = driver.find_element_by_id('session_key-login')
email.send_keys(EMAIL)

pwd = driver.find_element_by_id('session_password-login')
pwd.send_keys(PASSWORD)
driver.find_element_by_class_name('btn-primary').click()
print '[+] Logged in!!'
time.sleep(25)
##company = driver.find_element_by_id('advs-company')
##company.send_keys('apple')
##
##location = driver.find_element_by_css_selector('#advs-locationType > option:nth-child(2)')
##location.click()
##submit = driver.find_element_by_class_name('submit-advs')
##submit.click()

print '[+] Filters added!'
time.sleep(3)
people = driver.find_elements_by_css_selector('.mod.result')
print '[+] Search results received. Extracting data!'

count = 0
for p in people:
    try:
        count +=1
        img = p.find_element_by_class_name('result-image').get_attribute('href')
        name = p.find_element_by_css_selector('.title.main-headline').text
        profile_link = p.find_element_by_css_selector('.title.main-headline').get_attribute('href')
        description = p.find_element_by_css_selector('.description').text
        area = p.find_element_by_css_selector('.demographic').text
        df.loc[count] = [img, name, profile_link, description,  area]
        print name
        print df.shape
    except Exception,e:
        print str(e)

while count<200:
    nextpage = driver.find_element_by_css_selector('.next').find_element_by_css_selector('.page-link')
    nextpage.click()
    time.sleep(10)

    people = driver.find_elements_by_css_selector('.mod.result')
    print '[+] Search results received. Extracting data!'

    for p in people:
        try:
            count +=1
            img = p.find_element_by_class_name('result-image').get_attribute('href')
            name = p.find_element_by_css_selector('.title.main-headline').text
            profile_link = p.find_element_by_css_selector('.title.main-headline').get_attribute('href')
            description = p.find_element_by_css_selector('.description').text
            area = p.find_element_by_css_selector('.demographic').text
            df.loc[count] = [img, name, profile_link, description,  area]
            print df.shape
        except Exception,e:
            print str(e)

print df.shape
