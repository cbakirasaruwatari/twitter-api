#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import sys
import json
import ConfigParser
import traceback
import tweepy

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

cfg = ConfigParser.ConfigParser()
cfg.read('twitterApi.cfg')

class TwitterApi():

    def __init__(self) -> None:
        self.__load_cnf()

    def __load_cnf(self):
        self.__consumer_key = cfg.get("auth","consumer_key")
        self.__consumer_secret = cfg.get("auth","consumer_secret")
        self.__access_token  = cfg.get("auth","access_token")
        self.__access_token_secret = cfg.get("auth","access_token_secret")
        self.__auth = tweepy.OAuthHandler(self.__consumer_key,
                                          self.__consumer_secret
                                          ).set_access_token(self.__access_token,
                                                             self.__access_token_secret
                                                            )
        self._client = tweepy.API(self.__auth,wait_on_rate_limit = True)

class Tweet(TwitterApi):
    @retry
    def get_tweets(self,user_id: str) -> list:
       return [tweet for tweet in tweepy.Cursor(self._client.user_timeline,user_id = user_id,include_rts = True,exclude_replies=False).items()]

class User(TwitterApi):
    @retry
    def get_followers(self,user_id: list) -> list():
        return self._client.followers_ids(id=user_id)

class QueueingManager():
    def __init__(self,conn) -> None:
        raise NotImplementedError

def retry(func):
    def wrapper(*args, **kwargs):
        for c in range(2):
            try:
                func(*args, **kwargs)
            except Exception as e:
                if c==2:
                    traceback.print_exc()
                    sys.exit()
                else:
                    continue
    return wrapper
