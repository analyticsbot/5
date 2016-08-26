
from selenium import webdriver
from pyvirtualdisplay import Display
import time
display = Display(visible=0, size=(800, 600))
display.start()

while True:
    try:
        time.sleep(3600)
	print 'starting the web browser'
        driver = webdriver.Firefox()
        driver.get('http://162.243.104.58:8080/')
	time.sleep(10)
        driver.find_element_by_id('btn_submit').click()
        time.sleep(10)
        driver.close()
    except Exception,e:
        print str(e)
