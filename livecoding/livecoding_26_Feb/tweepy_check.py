from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy, atexit
import time

access_token = "4415348663-5pNNm5YQLmGrBMwWuJ1yObWbaESTIw1fNSPPDA9"
access_token_secret = "gafJtISvaAdfUWuc9xsSpY2R1rHu5ICbhQEMDmqG8SWT3"
consumer_secret = "1Qhn2zclLLAs82mQPEKeThJbS5CdCyYYsWtVvQi7S4oVCDdFJU"
consumer_key = "6FiPNQ2wpHQSiBB58m31V0l1v"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
    
api = tweepy.API(auth)

for friend in tweepy.Cursor(api.friends).items():
    # Process the friend here
    print(friend)
