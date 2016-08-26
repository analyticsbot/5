# import the tweepy library and required classes

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy

# your tokens for the app

access_token = "4415348663-5pNNm5YQLmGrBMwWuJ1yObWbaESTIw1fNSPPDA9"
access_token_secret = "gafJtISvaAdfUWuc9xsSpY2R1rHu5ICbhQEMDmqG8SWT3"

consumer_secret = "1Qhn2zclLLAs82mQPEKeThJbS5CdCyYYsWtVvQi7S4oVCDdFJU"
consumer_key = "6FiPNQ2wpHQSiBB58m31V0l1v"

# keywords to track
KEYWORDS = ['#python', '#java', '#javascript']

# class to listen to tweets in real time
# inherits tweepy's StreamListener class
class StdOutListener(StreamListener):
    def on_status(self, status):
        # Print the tweet
        global s
        s = status
        print(status.text)
        s.favorite_count
        s.retweet_count
        print api.retweet(s.id)
        print api.create_favorite(s.id)
        return False

    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True

    def on_timeout(self):
        return True

if __name__ == '__main__':
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    
    stream = Stream(auth, listener)
    stream.filter(track=KEYWORDS)
