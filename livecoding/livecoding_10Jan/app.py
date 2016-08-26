# -*- coding: cp1252 -*-
# import the Flask class from the flask module and other required modules
from flask import Flask, render_template, request, make_response, session, url_for, jsonify
import requests, threading, re, os, logging, gc, sqlite3
from random import choice 
from threading import Thread
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy, atexit
#from apscheduler.scheduler import Scheduler

## access tokens
access_token = "4415348663-5pNNm5YQLmGrBMwWuJ1yObWbaESTIw1fNSPPDA9"
access_token_secret = "gafJtISvaAdfUWuc9xsSpY2R1rHu5ICbhQEMDmqG8SWT3"
consumer_secret = "1Qhn2zclLLAs82mQPEKeThJbS5CdCyYYsWtVvQi7S4oVCDdFJU"
consumer_key = "6FiPNQ2wpHQSiBB58m31V0l1v"
HOURS = 24

# create the application object
app = Flask(__name__)
app.secret_key = "/\xfa-\x84\xfeW\xc3\xda\x11%/\x0c\xa0\xbaY\xa3\x89\x93$\xf5\x92\x9eW}"
app.WTF_CSRF_SECRET_KEY  = "secret_key"
app.CSRF_ENABLED = True
app.debug = True

##cron = Scheduler(daemon=True)
### Explicitly kick off the background thread
##cron.start()
##
##@cron.interval_schedule(hours=24)
##def job_function():
##    # Do your work here
##    pass

##
### Shutdown your cron thread if the web process is stopped
##atexit.register(lambda: cron.shutdown(wait=False))


# class to listen to tweets in real time
# inherits tweepy's StreamListener class
class StdOutListener(StreamListener):
    def on_status(self, status):
        # Print the tweet
        global s
        s = status
        print(status.text)
        #s.favorite_count
        #s.retweet_count
        print api.retweet(s.id)
        print api.create_favorite(s.id)

        #Check for tweets with livecoding.tv/ and like 1 out of every 4 tweets. 

        #Check for tweets with hashtags of all programming languages and frameworks.
        #Like tweets with at least 20 likes. Retweet tweets with at least 10 retweets

        #Check for tweets with keywords like “livestreaming code” “live programming”
        #but livecoding.tv/ missing and suggest Livecoding.tv to them.

        #Most popular tweets (Min 20 likes/ 10 RTS) from accounts we follow.
        #For every 10 tweets Retweet. For every 4 tweets, Like 1.
        
        return False

    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
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

def createProfile(p_name, keywords):
    c.execute("INSERT INTO keywords (profile_name, keywords) values(?, ?)", (p_name, keywords),)
    conn.commit()

def updateProfile(p_name, keywords):
    c.execute("UPDATE keywords set keywords= " + keywords + " where profile_name=" + p_name)
    conn.commit()

def accountsFollowed(arguments):
    pass

def likeTweetLivecoding(arguments):
    global liveCodingLikeMax, api
    liveCodingLikeMax = arguments[3]
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth)
    
    stream = Stream(auth, listener)
    stream.filter(track=KEYWORDS)

def workonTwitter(function, arguments):    
    if function == 'livecoding.tv':
        likeTweetLivecoding(arguments)
    if function == 'programming languages':
        programmingLanguages(arguments)
    if function == 'suggest Livecoding.tv':
        suggestLivecoding(arguments)
    if function == 'accounts we follow':
        accountsFollowed(arguments)
    
def main(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet):
    arguments = [keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet]
    threads= []

    threads.append(Thread(target = workonTwitter, args=(arguments)))
     
    for t in threads:
        t.start()
       
    return True

@app.route('/loadProfiles', methods=['GET'])
def loadProfiles():
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile_keywords.db')
    c = conn.cursor()
    c.execute("select profile_name, keywords, defaultProfile from keywords")
    data = c.fetchall()
    return render_template('profile.html', profiles = data)
    
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
    
def getParams(c, conn):
    c.execute("SELECT liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet from variables where id = 0")
    params = c.fetchone()
    return params

def getKeywordsProfile(profile, defaultProfileYN):
    if defaultProfileYN =='Y':
        c.execute("SELECT keywords from profile_keywords where default = 1")
        keywords = c.fetchall()
        return keywords
    else:
        c.execute("SELECT keywords from profile_keywords where profile = " + profile)
        keywords = c.fetchall()
        return keywords

def updateVariables(liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet):
    c.execute("UPDATE variables SET liveCodingLikeMin= " + str(liveCodingLikeMin) + \
              " liveCodingLikeMax = " + str(liveCodingLikeMin) +  \
              " programmingLanguagesMinLike = " + str(programmingLanguagesMinLike) + " programmingLanguagesMinRT = " + str(programmingLanguagesMinRT) +\
              " accountFollowedMinLike = " + str(accountFollowedMinLike) + " accountFollowedMinRT = " + str(accountFollowedMinRT) +\
              " accountFollowedLikeMin = " + str(accountFollowedLikeMin) + " liveCodingLikeMax = " + str(liveCodingLikeMin) +\
              " accountFollowedRTMin = " + str(accountFollowedRTMin) + " accountFollowedLikeMax = " + str(accountFollowedLikeMax) +\
              " accountFollowedRTMax = " + str(accountFollowedRTMax) + " accountFollowedRTMin = " + str(liveCodingLikeMin) +\
              " replyTweet = " + str(replyTweet) + " WHERE id=0;")
    conn.commit()

@app.route('/<profile>', methods=['GET'])    
@app.route('/', methods=['GET'])
def home(profile):
    """ flask view for the home page"""
    ## open connection to sqlite3 db
    conn = sqlite3.connect('profile_keywords.db')
    c = conn.cursor()
    #keywords = getKeywordsProfile(profile, 'Y')
    params = getParams(c, conn)
    liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet = params[0],params[1],params[2],params[3],params[4],\
                 params[5],params[6],params[7],params[8],params[9],params[10]
    keywords = 'aasa'
    return render_template('index.html', keywords = keywords, defaultProfile = 'Profile',\
                           liveCodingLikeMin= liveCodingLikeMin, liveCodingLikeMax=liveCodingLikeMax,\
                           programmingLanguagesMinLike = programmingLanguagesMinLike,
                 programmingLanguagesMinRT=programmingLanguagesMinRT, accountFollowedMinLike=accountFollowedMinLike,\
                           accountFollowedMinRT=accountFollowedMinRT,
                 accountFollowedLikeMin=accountFollowedLikeMin, accountFollowedLikeMax=accountFollowedLikeMax,\
                           accountFollowedRTMin=accountFollowedRTMin,
                 accountFollowedRTMax=accountFollowedRTMax, replyTweet = replyTweet)

def profileExists(profile):
    c.execute("SELECT keywords from keywords where profile_keywords = " + str(profile))
    keywords = c.fetchone()
    if keywords == None:
        return False
    else:
        return True
    
@app.route('/go', methods=['GET', 'POST'])
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

        print keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet

        ## add all variables to session
        session['keywords'] = keywords
        session['profile'] = profile
        session['liveCodingLikeMin'] = liveCodingLikeMin
        session['liveCodingLikeMax'] = liveCodingLikeMax
        session['programmingLanguagesMinLike'] = programmingLanguagesMinLike
        session['programmingLanguagesMinRT'] = programmingLanguagesMinRT
        session['accountFollowedMinLike'] = accountFollowedMinLike
        session['accountFollowedMinRT'] = accountFollowedMinRT
        session['accountFollowedLikeMin'] = accountFollowedLikeMin
        session['accountFollowedLikeMax'] = accountFollowedLikeMax
        session['accountFollowedRTMin'] = accountFollowedRTMin
        session['accountFollowedRTMax'] = accountFollowedRTMax
        session['replyTweet'] = replyTweet
       
        
        if (keywords != ''):
            gc.collect()
            ## call the threads
            updateVariables(liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet)

            if profileExists(profile):
                updateProfile(profile, keywords)
            else:
                createProfile(p_name, keywords)
            
            main(keywords, profile, liveCodingLikeMin, liveCodingLikeMax,programmingLanguagesMinLike,\
                 programmingLanguagesMinRT, accountFollowedMinLike, accountFollowedMinRT,\
                 accountFollowedLikeMin, accountFollowedLikeMax, accountFollowedRTMin,\
                 accountFollowedRTMax, replyTweet)
            
            flash('Working on the profile')
        else:
            errors =  {'error': 'keywords required'}
        
        return render_template('index.html', title = 'Livecoding Twitter Bot | ' + str(profile), \
               keywords = keywords, errors = errors, defaultProfile = 'Profile')  

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
