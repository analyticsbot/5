# -*- coding: cp1252 -*-
# import the Flask class from the flask module and other required modules
from flask import Flask, render_template, request, make_response, session, url_for, jsonify, flash
import requests, threading, re, os, logging, gc, sqlite3, time
from datetime import datetime
from random import choice 
from threading import Thread
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy, atexit
from unidecode import unidecode
from apscheduler.schedulers.blocking import BlockingScheduler

## declare static variables

## access tokens from twitter
access_token = "4415348663-Zuk3qz3CAQdsrdbcIyUe8UnIcFq3SvMrla9ooZV"
access_token_secret = "1StiYbP497HOzqXX0c8GVqxoZu0qNceAN0HHQPyCPZRXE"
consumer_secret = "0Q2uAPUZ9Dny9SKeHFQ684eGJsI4ZMAP5htJ2Af91z2ygRIdx9"
consumer_key = "ur9NcowJYOBXKgd45XPIFADmc"
HOURS = 24
screen_name = 'NowLivecodingtv'

# create the application object
app = Flask(__name__)
app.secret_key = "/\xfa-\x84\xfeW\xc3\xda\x11%/\x0c\xa0\xbaY\xa3\x89\x93$\xf5\x92\x9eW}"
app.WTF_CSRF_SECRET_KEY  = "secret_key"
app.CSRF_ENABLED = True
app.debug = True

## scheduler that runs every 24 hours and likes/RTs tweets
sched = BlockingScheduler()
@sched.scheduled_job('interval', hours = HOURS)
def timed_job():
    likeTweetTimelineTweets()
    
def in24Hours(d):
    """function to check if the tweet is older than a day/24 hours"""
    age = int(time.time() - (d - datetime(1970,1,1)).total_seconds())
    return age<86400

def likeTweetTimelineTweets():
    """Function to like/ RT timeline tweets from the accounts being followed by
    NowLivecodingtv handle. This is called every 24 hours"""
    #initialize a list to hold all the tweepy Tweets
    alltweets = []	
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    ## store all the tweets made within 24 hours
    tweets_within_24_hours = []
    for t in new_tweets:
        if in24Hours(t.created_at):
            tweets_within_24_hours.append(t)        
    
    #save most recent tweets
    alltweets.extend(tweets_within_24_hours)

    ## if there are more tweets within 24 hours
    if len(tweets_within_24_hours) == len(new_tweets):    
        #save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        continue_ = True
        
        #keep grabbing tweets until there are no tweets left to grab or 24 hour window is crossed
        while (len(new_tweets) > 0) and continue_:                
                #all subsiquent requests use the max_id param to prevent duplicates
                new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
                
                #save most recent tweets
                alltweets.extend(new_tweets)

                for t in new_tweets:
                    if in24Hours(t.created_at):
                        tweets_within_24_hours.append(t)
                    else:
                        continue_ = False
                
                #update the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1

    #Most popular tweets (Min 20 likes/ 10 RTS) from accounts we follow.
    #For every 10 tweets Retweet. For every 4 tweets, Like 1.
    rt_count = 0
    lk_count = 0
    for tweet in tweets_within_24_hours:
        if tweet.favorite_count>int(dd.get('accountFollowedMinLike', 20)):
            print 'RRRT'
            if lk_count %dd.get('accountFollowedLikeMax', 4)==0:
                api.create_favorite(tweet.id)
            lk_count +=1
        if tweet.retweet_count>int(dd.get('accountFollowedMinRT', 10)):
            print 'FFF'
            if rt_count %dd.get('accountFollowedRTMax', 10)==0:
                api.retweet(tweet.id)
            rt_count +=1

def createProfile(p_name, keywords, c, conn):
    """Function to create a new profile if it does not exist"""
    c.execute("INSERT INTO keywords (profile_name, keywords) values(?, ?)", (p_name, keywords),)
    conn.commit()

def updateProfile(p_name, keywords, c, conn):
    """Function to create a new profile if it it exists"""
    c.execute("UPDATE keywords set keywords= '" + keywords + "' where profile_name= '" + p_name +"'")
    conn.commit()

## declare a global vairable that will host the input values to be passed among functions
global dd
dd = {'livecoding_like_cnt':0}
programmingLanguages = ['Python']
# class to listen to tweets in real time
# inherits tweepy's StreamListener class
class StdOutListener(StreamListener):
    def on_status(self, status):
        # Print the tweet
        tweet = status.text
        #print str(unidecode(tweet))
        print 'listening'
        #Check for tweets with livecoding.tv/ and like 1 out of every 4 tweets. 
        if ('livecoding.tv' in tweet):
            if dd['livecoding_like_cnt'] % int(dd.get('liveCodingLikeMax', 4)) ==0:
                print 'live coding'
                api.create_favorite(status.id)
            dd['livecoding_like_cnt'] +=1             
            
        #Check for tweets with hashtags of all programming languages and frameworks.
        #Like tweets with at least 20 likes. Retweet tweets with at least 10 retweets
        if any(ext in tweet for ext in str((dd['keywords'])).split(',')):
            print 'RT'
            if status.favorite_count >int(dd.get('programmingLanguagesMinLike', 20)):
                api.create_favorite(status.id)
                print 'programmingLanguagesMinLike'
            if status.retweet_count>int(dd.get('programmingLanguagesMinRT', 10)):
                api.retweet(status.id)
                print 'programmingLanguagesMinRT'

        #Check for tweets with keywords like “livestreaming code” “live programming”
        #but livecoding.tv/ missing and suggest Livecoding.tv to them.
        if ('livestreaming code' in tweet) and ('live programming' in tweet) and ('livecoding.tv' not in tweet):
            print dd['replyTweet']
            api.update_status(dd['replyTweet'], in_reply_to_status_id = status.id)
        
        return True

    def on_error(self, status_code):
        #print('Got an error with status code: ' + str(status_code))
        return True

    def on_timeout(self):
        return True

try:
    if os.environ['Production'] == 'True':
        app.debug = False
except Exception,e:
    print str(e)

## open connection to sqlite3 db
conn = sqlite3.connect('profile_keywords.db')
c = conn.cursor()

def likeTweetLivecoding(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet):
    """Function to start the tweepy stream on button click"""
    global api
    dd['replyTweet'] = replyTweet
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth, wait_on_rate_limit = True)
    keywords = str((dd['keywords'])).split(',') + ['livestreaming code', 'live programming', 'livecoding.tv']
    print keywords
    stream = Stream(auth, listener)
    stream.filter(languages=["en"], track=keywords)

def likeTweetProgrammingLang(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet):

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth, wait_on_rate_limit = True)
    ## store all the tweets made within 24 hours
    tweets_within_24_hours = []
        
    for query in keywords.split(','):
        for tweet in tweepy.Cursor(api.search, q=query, count=100, result_type="recent", include_entities=True, lang="en").items():
            if in24Hours(tweet.created_at):
##                print str(unidecode(tweet.text)),'\n', dd.get('programmingLanguagesMinLike'), dd.get('programmingLanguagesMinRT')
##                print (tweet.favorite_count), (tweet.favorite_count>=int(dd.get('programmingLanguagesMinLike')))
##                print tweet.retweet_count>=int(dd.get('programmingLanguagesMinRT'))
                print 'programming tweet', int(dd.get('programmingLanguagesMinLike'))
                if tweet.favorite_count>=int(dd.get('programmingLanguagesMinLike')):
                    print tweet.id
                    try:
                        api.create_favorite(tweet.id)
                    except Exception,e:
                        print str(e)
                        pass
                    #lk_count +=1
                if tweet.retweet_count>=int(dd.get('programmingLanguagesMinRT')):
                    try:
                        api.retweet(tweet.id)
                    except Exception,e:
                        print str(e)
                        pass
                    #rt_count +=1
                
            else:
                break

##    #Most popular tweets (Min 20 likes/ 10 RTS) from accounts we follow.
##    #For every 10 tweets Retweet. For every 4 tweets, Like 1.
##    rt_count = 0
##    lk_count = 0
##    for tweet in tweets_within_24_hours:
##        #print 'yaya', dd.get('programmingLanguagesMinLike'), tweet.favorite_count>=0,  tweet.id
##        print api.create_favorite(tweet.id), api.retweet(tweet.id)
##        if tweet.favorite_count>=dd.get('programmingLanguagesMinLike'):
##            #print tweet.id
##            #print api.create_favorite(tweet.id)
##            lk_count +=1
##        if tweet.retweet_count>=dd.get('programmingLanguagesMinRT'):
##            api.retweet(tweet.id)
##            rt_count +=1

def workonTwitter(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet):
    likeTweetLivecoding(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet)

def main(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet):
    """Function for multithreading. This is need as threads start at backend and the control
        is again passed back to the user"""
    arguments = [keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet]
    threads= []

    threads.append(Thread(target = workonTwitter, args=(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet)))
    threads.append(Thread(target = likeTweetProgrammingLang, args=(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet)))
     
    for t in threads:
        t.start()

def getParams(c, conn):
    """Function to get the parameter"""
    c.execute("SELECT liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet from variables where id = 0")
    params = c.fetchone()
    return params


def updateVariables(liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet, c, conn):
    """Function to update the variables"""
    c.execute("UPDATE variables SET liveCodingLikeMin = " + str(liveCodingLikeMin) + \
              ", liveCodingLikeMax = " + str(liveCodingLikeMax) +  \
              ", programmingLanguagesMinLike = " + str(programmingLanguagesMinLike) + ", programmingLanguagesMinRT = " + str(programmingLanguagesMinRT) +\
              ", accountFollowedMinLike = " + str(accountFollowedMinLike) + ", accountFollowedMinRT = " + str(accountFollowedMinRT) +\
              ", accountFollowedLikeMin = " + str(accountFollowedLikeMin) + ", liveCodingLikeMax = " + str(liveCodingLikeMin) +\
              ", accountFollowedRTMin = " + str(accountFollowedRTMin) + ", accountFollowedLikeMax = " + str(accountFollowedLikeMax) +\
              ", accountFollowedRTMax = " + str(accountFollowedRTMax) + ", accountFollowedRTMin = " + str(liveCodingLikeMin) +\
              ", replyTweet = '" + str(replyTweet) + "' WHERE id=0;")
    conn.commit()

def getKeywordsProfile(profile, conn, c):
    """Function to get keywords associated with particular profiles"""
    if profile == None:
        c.execute("SELECT keywords from keywords where defaultProfile = 1")
        keywords = c.fetchall()
        return keywords
    else:
        c.execute("SELECT keywords from keywords where profile_name = '" + profile + "'")
        keywords = c.fetchall()
        return keywords

def getDefaultProfile(conn, c):
    """Function to get the default profile"""
    c.execute("SELECT profile_name from keywords where defaultProfile = 1")
    profile = c.fetchone()
    return profile    

def profileExists(profile, c, conn):
    """Function to check whether the profile exists"""
    c.execute("SELECT keywords from keywords where profile_name = '" + str(profile) + "'")
    keywords = c.fetchone()
    if keywords == None:
        return False
    else:
        return True

## view for a display. Homepage
@app.route('/profile/<profile>', methods=['GET'])    
@app.route('/', methods=['GET'])
def home(profile=None):
    """ flask view for the home page"""
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile_keywords.db')
    c = conn.cursor()

    if not profile:
        profile = getDefaultProfile(conn, c)[0]
    
    keywords = ''.join(getKeywordsProfile(profile, conn, c)[0])
    
    params = getParams(c, conn)
    liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet = params[0],params[1],params[2],params[3],params[4],\
                 params[5],params[6],params[7],params[8],params[9],params[10]
    
    return render_template('index.html', keywords = keywords, defaultProfile = profile,\
                           liveCodingLikeMin= liveCodingLikeMin, liveCodingLikeMax=liveCodingLikeMax,\
                           programmingLanguagesMinLike = programmingLanguagesMinLike,
                 programmingLanguagesMinRT=programmingLanguagesMinRT, accountFollowedMinLike=accountFollowedMinLike,\
                           accountFollowedMinRT=accountFollowedMinRT,
                 accountFollowedLikeMin=accountFollowedLikeMin, accountFollowedLikeMax=accountFollowedLikeMax,\
                           accountFollowedRTMin=accountFollowedRTMin,
                 accountFollowedRTMax=accountFollowedRTMax, replyTweet = replyTweet, profile = profile)

## view for load all profiles
@app.route('/loadProfiles', methods=['GET'])
def loadProfiles():
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile_keywords.db')
    c = conn.cursor()
    c.execute("select profile_name, keywords, defaultProfile from keywords")
    data = c.fetchall()
    return render_template('profile.html', profiles = data)

## view for making a profile default   
@app.route('/makedefault/<profile>', methods=['GET', 'POST'])
def makeDefault(profile):
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile_keywords.db')
    c = conn.cursor()
    c.execute("UPDATE keywords SET defaultProfile=0")
    conn.commit()
    c.execute("UPDATE keywords SET defaultProfile = 1 where profile_name = '" + str(profile) + "'")
    conn.commit()
    c.execute("select profile_name, keywords, defaultProfile from keywords")
    data = c.fetchall()
    return render_template('profile.html', profiles = data)

## view for the post object
@app.route('/go', methods=['POST'])
def go():
    """ flask view for the search page"""
    if request.method == "POST":
        errors = {}
        profile = request.form['profile']
        keywords = request.form['keywords']
        
        liveCodingLikeMin = request.form['liveCodingLikeMin']
        liveCodingLikeMax = request.form['liveCodingLikeMax']
        
        programmingLanguagesMinLike = request.form['programmingLanguagesMinLike']
        programmingLanguagesMinRT = request.form['programmingLanguagesMinRT']
        
        accountFollowedMinLike = request.form['accountFollowedMinLike']
        accountFollowedMinRT = request.form['accountFollowedMinRT']
        
        accountFollowedLikeMin = request.form['accountFollowedLikeMin']
        accountFollowedLikeMax = request.form['accountFollowedLikeMax']
        
        accountFollowedRTMin = request.form['accountFollowedRTMin']
        accountFollowedRTMax = request.form['accountFollowedRTMax']
        
        replyTweet = request.form['replyTweet']


        ## add all variables to session
        dd['keywords'] = unidecode(keywords)
        dd['profile'] = profile
        dd['liveCodingLikeMin'] = liveCodingLikeMin
        dd['liveCodingLikeMax'] = liveCodingLikeMax
        dd['programmingLanguagesMinLike'] = programmingLanguagesMinLike
        dd['programmingLanguagesMinRT'] = programmingLanguagesMinRT
        dd['accountFollowedMinLike'] = accountFollowedMinLike
        dd['accountFollowedMinRT'] = accountFollowedMinRT
        dd['accountFollowedLikeMin'] = accountFollowedLikeMin
        dd['accountFollowedLikeMax'] = accountFollowedLikeMax
        dd['accountFollowedRTMin'] = accountFollowedRTMin
        dd['accountFollowedRTMax'] = accountFollowedRTMax
        dd['replyTweet'] = replyTweet

        ## open connection to sqlite3 db
        conn = sqlite3.connect('profile_keywords.db')
        c = conn.cursor()
        
        if (keywords != ''):
            gc.collect()
            ## call the threads
            updateVariables(liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet,c, conn)

            if profileExists(profile, c, conn):
                updateProfile(profile, keywords, c, conn)
            else:
                createProfile(profile, keywords, c, conn)
            
            main(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet)
            
            flash('Working....')
        else:
            errors =  {'error': 'keywords required'}
        
        return render_template('index.html', title = 'Livecoding Twitter Bot | ' + str(profile), \
               keywords = keywords, errors = errors, defaultProfile = profile,\
                           liveCodingLikeMin= liveCodingLikeMin, liveCodingLikeMax=liveCodingLikeMax,\
                           programmingLanguagesMinLike = programmingLanguagesMinLike,
                 programmingLanguagesMinRT=programmingLanguagesMinRT, accountFollowedMinLike=accountFollowedMinLike,\
                           accountFollowedMinRT=accountFollowedMinRT,
                 accountFollowedLikeMin=accountFollowedLikeMin, accountFollowedLikeMax=accountFollowedLikeMax,\
                           accountFollowedRTMin=accountFollowedRTMin,
                 accountFollowedRTMax=accountFollowedRTMax, replyTweet = replyTweet, profile = profile)  

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port = 5500)
