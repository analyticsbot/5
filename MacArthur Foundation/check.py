# -*- coding: cp1252 -*-
from bs4 import BeautifulSoup
import requests, re, json, string, sys
from newspaper import Article
from text_unidecode import unidecode
import pandas as pd

##possible state names
states = [

         'Alabama','Alaska','Arizona','Arkansas','California','Colorado',
         'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho', 
         'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana',
         'Maine' 'Maryland','Massachusetts','Michigan','Minnesota',
         'Mississippi', 'Missouri','Montana','Nebraska','Nevada',
         'New Hampshire','New Jersey','New Mexico','New York',
         'North Carolina','North Dakota','Ohio',    
         'Oklahoma','Oregon','Pennsylvania','Rhode Island',
         'South  Carolina','South Dakota','Tennessee','Texas','Utah',
         'Vermont','Virginia','Washington','West Virginia',
         'Wisconsin','Wyoming'
    ]

## valid chars for file names
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

df = pd.DataFrame(columns = ['fellow_name','fellow_title', 'pub_date',\
                             'fellow_designation','fellow_school','fellow_location',\
                             'fellow_age','fellow_deceased'])
def getFellowData(id, states, valid_chars, df):
    """Function to pull data on fellows"""
    url = 'https://www.macfound.org/fellows/' + str(id) + '/'
    resp = requests.get(url)
    if 'Sorry' in unidecode(resp.text):
        print 'No more fellows to scrape. Exiting'
        sys.exit(1) ## Exit when no more profiles exist
    soup = BeautifulSoup(unidecode(resp.text))
    fellow_information =soup.find(attrs={'class':'fellow-information'})
    try:
        fellow_name = fellow_information.find('h1').getText()
    except:
        fellow_name = ''
    try:
        fellow_title = fellow_information.find('h3').getText()
    except:
        fellow_title = ''
    try:
        pub_date = str(fellow_information.find('h6').getText()).replace('Published','').strip()
    except:
        pub_date = ''
    fellow_designation = ''
    fellow_school = ''
    fellow_location = ''
    fellow_age = ''
    fellow_deceased = ''
    try:
        p_tags = fellow_information.findAll('p')
        for tag in p_tags:
##            val = tag.getText().split(',')[-1].strip()
##            if 'Professor' in tag.getText():
##                fellow_designation = tag.getText()
##                ix = p_tags.index(tag)
##                fellow_school = p_tags[ix+1].getText()
##            elif val in states:
##                fellow_location = tag.getText()
            if 'Age' in tag.getText():
                fellow_age = re.findall(r'\d+', tag.getText())[0]
                ix = p_tags.index(tag)
                fellow_location = p_tags[ix-1].getText()
                if ix-2>=0 :
                    fellow_school = p_tags[ix-2].getText()
                else:
                    fellow_school = ''
                if ix-3>=0 :
                    fellow_designation = p_tags[ix-3].getText()
                else:
                    fellow_designation = ''
            elif 'Deceased' in tag.getText():
                fellow_deceased = tag.getText().replace('Deceased:', '')
##            if 'University' in tag.getText():
##                fellow_school = tag.getText()
##                ix = p_tags.index(tag)
##                fellow_designation = p_tags[ix-1].getText()
    except:
        pass
    
    nrows = df.shape[0]
    print [fellow_name,fellow_title, pub_date,\
                             fellow_designation,fellow_school,fellow_location,\
                             fellow_age,fellow_deceased]
    df.loc[nrows+1] = [fellow_name,fellow_title, pub_date,\
                             fellow_designation,fellow_school,fellow_location,\
                             fellow_age,fellow_deceased]
    
    
for i in range(738, 739):
    print i
    getFellowData(i, states, valid_chars, df)

#df.to_csv('fellows2.csv', index = False, encoding = 'utf-8')
