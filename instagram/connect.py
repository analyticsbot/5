

from instagram.client import InstagramAPI
##access_token = "593674689.02ce2b1.cb812cd9bef24efda4ed366e7e9ff252"
##api = InstagramAPI(access_token=access_token)
##user_info = api.user('nearthesea05')
##print user_info
##
##
##from instagram.client import InstagramAPI
##
##access_token = "593674689.02ce2b1.cb812cd9bef24efda4ed366e7e9ff252"
##client_secret = "02ce2b14d61c4100993363c9af9978a8"
##api = InstagramAPI(access_token=access_token, client_secret=client_secret)
##recent_media, next_ = api.user_recent_media(user_id='nearthesea05', count=10)
##for media in recent_media:
##   print media.caption.text
##
##user_followers, next_ = api.user_followed_by(user_id='nearthesea05')
##while next_:
##    more_user_followers, next_ = api.user_followed_by(with_next_url=next_) #this will get you all your followers
##    user_followers.extend(more_user_followers)
##
##len(user_followers) #this is the numbers of followers you have

#!/usr/bin/env python

"""Follows Instagram users with similar taste and likes their photos.

Scrapes users who have liked a seed user's recent photos (avoiding
users whose profiles seem spammy), then likes some of their most
popular recent photos and follows them. After 3 days, unfollows them.

Required modules:
    httplib2
    simplejson

Version: 2.1.8

Licensed under a BSD New license.

Uses the https://github.com/Instagram/python-instagram client.
by Spike Padley, 2014.
"""

import json
import logging
import os
import random
import re
import time
from instagram import client

# CUSTOMISABLE
CONFIG = {
    'client_id': '',
    'client_secret': '',
    'redirect_uri': '',
    'access_token': '',
    'client_ips': ''
}
SEED_USER = 'society6'
NUM_TO_FOLLOW = 25
NUM_TO_UNFOLLOW = 25
# END CUSTOMISABLE

# Logging stuff
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global declarations
TILES_PATH = os.getcwd()+'/Tiles.json'


def username_to_id(username):
    """Accepts a username and returns its ID."""
    user = api.user_search(q=username, count=1)
    if username != user[0].username:
        logger.error('Username to ID failed')
    return user[0].id

access_token = "593674689.02ce2b1.cb812cd9bef24efda4ed366e7e9ff252"
client_secret = "02ce2b14d61c4100993363c9af9978a8"
api = InstagramAPI(access_token=access_token, client_secret=client_secret)

print username_to_id('society6')

"""
def check_user(user, ids_to_avoid=[]):  # TODO: Check user not super popular
    ""Checks if user meets criteria to be followed, returns boolean.

    Args:
    user (object): An instagram.models.User object
    ids_to_avoid (list): IDs to avoid, defaults to empty list
    ""
    if (
        user.profile_picture != 'http://images.ak.instagram.com/profiles/anonymousUser.jpg'
        and user.full_name
        and user.bio
        and re.search(r'follow|f4f|1D|one ?direction|bieber|shout', user.bio, re.I) is None
        and user.id not in ids_to_avoid
    ):
        rel = api.user_relationship(user_id=user.id)
        if (
            rel.outgoing_status == 'none'
            and rel.incoming_status != 'followed_by'
            and rel.target_user_is_private is False
        ):
            return True
    else:
        return False

try:
    while True:

        api = client.InstagramAPI(**CONFIG)

        # Load Tiles.json
        tiles = {}
        with open(TILES_PATH) as f:
            tiles = json.load(f)

        # Make a list of users who are currently being followed, or have been followed before
        already_followed = []
        for tile in tiles['present']:
            already_followed.append(tile['user_id'])
        for tile in tiles['past']:
            already_followed.append(tile['user_id'])

        # Scrape users
        scraped_users = []

        def scrape_users():
            next_url = ''
            while len(scraped_users) < NUM_TO_FOLLOW:

                recent_media, next_url = api.user_recent_media(user_id=username_to_id(SEED_USER), count=2, with_next_url=next_url)
                for media in recent_media:

                    likes = api.media_likes(media_id=media.id)
                    for user in likes:

                        if check_user(user=user, ids_to_avoid=(already_followed + scraped_users)):

                            scraped_users.append(user.id)
                            logger.info('Scraped user ' + user.id)

                            if len(scraped_users) >= NUM_TO_FOLLOW:
                                return
                        else:
                            logger.info('Avoided user ' + user.id)
        scrape_users()

        logger.info('Following and liking the photos of %s users', len(scraped_users))

        # Loop through scraped_users and like their photos and follow them
        for user_id in scraped_users:
            try:
                recent_media, next_url = api.user_recent_media(user_id=user_id, count=12)

                media_dict = {}
                for media in recent_media:
                    media_dict[media.like_count] = media.id

                i = 1
                for likes in sorted(media_dict.keys(), reverse=True):

                    if not 0 < likes < 300:
                        continue

                    if (random.random() + (i / (1 / 0.07))) < 0.5 or i <= 2:

                        api.like_media(media_id=media_dict[likes])  # like_media doesn't return anything?
                        logger.info('Liked media ' + media_dict[likes])
                        time.sleep(random.randint(20, 50))

                    i += 1

                follow = api.follow_user(user_id=user_id)
                if follow[0].outgoing_status != 'none':

                    tiles['present'].append({'user_id': user_id, 'time_followed': time.time()})
                    logger.info('Followed user ' + user_id)

            except Exception, e:
                logger.error(e)

        # Work out who (if anyone) is due for unfollowing
        to_unfollow = []
        for tile in tiles['present']:
            if (time.time() - tile['time_followed']) > (60 * 60 * 24 * 3):
                    to_unfollow.append(tile)
                    if len(to_unfollow) >= NUM_TO_UNFOLLOW:
                        break

        logger.info('Unfollowing %s users', len(to_unfollow))

        # Unfollow users due for unfollowing
        for tile in to_unfollow:
            try:
                unfollow = api.unfollow_user(user_id=tile['user_id'])
                if unfollow[0].outgoing_status == 'none':

                    tiles['present'].remove(tile)
                    tiles['past'].append(tile)
                    logger.info('Unfollowed user ' + tile['user_id'])

            except Exception, e:
                logger.error(e)

        with open(TILES_PATH, 'w') as f:
            json.dump(tiles, f)

        logger.info('Waiting 1 hour until repeat')
        time.sleep(60 * 60)

except KeyboardInterrupt:
    # ^C exits the script: Save Tiles.json first
    with open(TILES_PATH, 'w') as f:
        json.dump(tiles, f)
    logger.info('Saved and exited')
"""
