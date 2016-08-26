from selenium import webdriver
import os, shutil, time
from PyPDF2 import PdfFileReader, PdfFileMerger

INITIAL_DEST_FOLDER = 'C:\\Users\\Ravi Shankar\\Documents\\Upwork\\law firm\\initial_dest\\'
FINAL_DEST_FOLDER = 'C:\\Users\\Ravi Shankar\\Documents\\Upwork\\law firm\\final\\'

## profile of firefox
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", INITIAL_DEST_FOLDER)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

driver  = webdriver.Firefox(firefox_profile=profile)
url = 'https://proview.thomsonreuters.com/timeout.html?sourceURL=http%3A%2F%2Fproview.thomsonreuters.com%2Flibrary.html%3Flanguage%3Den_US'
email = 'rosenblumlawfirm1'
pwd = 'tester@1!'
driver.get(url)
time.sleep(3)
username = driver.find_element_by_id('j_username')
username.send_keys(email)

password = driver.find_element_by_id('j_password')
password.send_keys(pwd)

login = driver.find_element_by_css_selector('.loginButton.loginOrangeButton')
login.click()
time.sleep(10)
a = driver.find_elements_by_class_name('titleCover')
a[2].click()
time.sleep(3)

count = 0
while True:
    try:
        print 'Getting page :: ', count
        driver.find_element_by_id('createAndShareButton').click()
        create = driver.find_element_by_id('createAndShareNextButton')
        create.click()
        time.sleep(3)
        ## get file in the initial download folder
        filename = listdir(INITIAL_DEST_FOLDER)[0]
                
        ## rename the file to SKU name
        os.rename(filename, str(count) + '.pdf')

        shutil.move(INITIAL_DEST_FOLDER + '/' + str(count) + '.pdf', FINAL_DEST_FOLDER + '/')

        nxt = driver.find_element_by_id('nextP1Click')
        nxt.click()
        time.sleep(3)

        count +=1
    except Exception,e:
        print str(e)
        break

pdf_files = [f for f in os.listdir(FINAL_DEST_FOLDER) if f.endswith("pdf")]
merger = PdfFileMerger()

for filename in pdf_files:
    merger.append(PdfFileReader(os.path.join(FINAL_DEST_FOLDER, filename), "rb"))

merger.write(os.path.join(FINAL_DEST_FOLDER, "merged_full.pdf"))
