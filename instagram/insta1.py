from instagram.client import InstagramAPI
access_token = "593674689.02ce2b1.cb812cd9bef24efda4ed366e7e9ff252"
api = InstagramAPI(access_token=access_token)
user_info = api.user('society6')
print user_info
