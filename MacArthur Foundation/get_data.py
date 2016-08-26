# -*- coding: cp1252 -*-
from bs4 import BeautifulSoup
import requests, re, json, string, sys
from newspaper import Article
from text_unidecode import unidecode
import pandas as pd

## valid chars for file names
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
df = pd.DataFrame(columns = ['fellow_name','fellow_title', 'pub_date',\
                             'fellow_designation','fellow_school','fellow_location',\
                             'fellow_age','fellow_deceased', 'fellow_url'])

def getFellowData(id, valid_chars, df):
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
    except:
        pass

    nrows = df.shape[0]
    df.loc[nrows+1] = [fellow_name,fellow_title, pub_date,\
                             fellow_designation,fellow_school,fellow_location,\
                             fellow_age,fellow_deceased, url]

    try:
        fellow_article_body = unidecode(soup.find('div', attrs = {'class':'fellow-profile-bio user-generated clearfix'}).getText())
    except:
        fellow_article_body = ''
    
    c = 0
    fellow_photos = {}
    try:
        photos = soup.findAll('li', attrs = {'class':'media'})
        for p in photos:
            fellow_photos['photo_' + str(c)] =  'https://www.macfound.org' + p.find('a')['href']
            c+=1
    except:
        pass

    try:
        fellow_additional_information = soup.find('div', attrs = {'class':'fellow-additional-information'}).find('a')['href']
    except:
        fellow_additional_information = ''

    ## write the fellow summary to file
    f = open(fellow_name.replace(' ', '_') + '_summary.json', 'wb')
    data = {'fellow_name':fellow_name,'fellow_title':fellow_title, 'pub_date':pub_date,\
            'fellow_designation' : fellow_designation, 'fellow_school':fellow_school,\
            'fellow_location':fellow_location, 'fellow_age':fellow_age, 'fellow_deceased':fellow_deceased,\
            'fellow_photos':str(fellow_photos), 'fellow_additional_information':fellow_additional_information,\
            'fellow_url':url, 'fellow_article_body':fellow_article_body}
    f.write(json.dumps(data))
    f.close()

    ## write the fellow media summary to file
    fellow_articles = soup.findAll(attrs = {'class':'promo default in-the-media '})

    for articles in fellow_articles:
        link  = articles.find('a', attrs = {'class':'icon'})['href']
        title = unidecode(articles.find('h3').getText())
        file_name = fellow_name.replace(' ', '_') + '_media_'+ title.replace(' ', '_') + '.json'
        file_name = ''.join(c for c in file_name if c in valid_chars)
        f = open(file_name, 'wb')
        article = Article(link)
        article.download()
        article.parse()

        article_authors = str(article.authors)
        article_publish_date = str(article.publish_date)
        article_text = unidecode(article.text)
        article_top_image = article.top_image
        article_videos = article.movies
        article_title = article.title
        article_all_images = str(article.images)
        article_keywords = str(article.keywords)
        article_tags = str(list(article.tags))

        article_data = {'article_link':link, 'title':title, 'article_authors':article_authors,\
                        'article_publish_date':article_publish_date, 'article_text':article_text,\
                        'article_top_image':article_top_image, 'article_videos':article_videos,\
                        'article_title':article_title, 'article_all_images':article_all_images,\
                        'article_keywords':article_keywords, 'article_tags':article_tags}
        f.write(json.dumps(article_data))
        f.close()
    
for i in range(1, 100):
    getFellowData(i, valid_chars, df)

df.to_csv('fellows_information.csv', index = False, encoding = 'utf-8')
