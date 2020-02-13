#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import json
import logging
import time
import traceback
import configparser

import mysql.connector as mydb
import tweepy

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

setting_path='../resource/twitter_api.cfg'
if os.path.isfile(setting_path) is False:
    raise FileNotFoundError
cfg = configparser.SafeConfigParser(os.environ)
cfg.read(setting_path)

def retry_api(func):
    def wrapper(*args, **kwargs):
        for c in range(2):
            try:
                func(*args, **kwargs)
            except Exception as e:
                if c==2:
                    logger.critical("getting connect twitter api, something wrong")
                    sys.exit()
                else:
                    traceback.print_exc()
                    continue
    return wrapper

class DBConnector():
    def connect(self):
        self.conn = mydb.connect(
        host=cfg["persistance_db"]["db_host"],
        port=cfg["persistance_db"]["db_port"],
        user=cfg["persistance_db"]["db_user"],
        password=cfg["persistance_db"]["db_password"],
        database=cfg["persistance_db"]["db_name"]
        )
        self.cursor = self.conn.cursor()
    def close(self):
        self.conn.close()
        self.cursor.close()
    def commit(self):
        self.conn.commit()   
    def rollback(self):
         self.conn.rollback()

class QueingDBConnector():
    
    def connect(self):
        self.conn = mydb.connect(
        host=cfg["persistance_db"]["db_host"],
        port=cfg["persistance_db"]["db_port"],
        user=cfg["persistance_db"]["db_user"],
        password=cfg["persistance_db"]["db_password"],
        database=cfg["persistance_db"]["db_name"]
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()
        self.cursor.close()

class TwitterApi():
    db=DBConnector()
    def __init__(self) -> None:
        self.__load_cfg()
    def __load_cfg(self):
        self.__consumer_key = cfg["auth"]["consumer_key"]
        self.__consumer_secret = cfg["auth"]["consumer_secret"]
        self.__access_token  = cfg["auth"]["access_token"]
        self.__access_token_secret = cfg["auth"]["access_token_secret"]
        self.__auth = tweepy.OAuthHandler(self.__consumer_key,
                                          self.__consumer_secret
                                          )
        self.__auth.set_access_token(self.__access_token,self.__access_token_secret)
        self._client = tweepy.API(self.__auth,wait_on_rate_limit = True)

class Tweet(TwitterApi):

    def register_tweet(self) -> str:
        '''
        read user (db) & fetch tweet (api) & register db.
        '''
        while True:
            userids = self.read_target_user()
            logger.info("START USERS:" + str(userids))
            for userid in userids:
                t = self.fetch_post(userid)
                posts,api_code = t["posts"],t["api_code"]
                if len(posts) == 0:
                    continue
                self.insert_tweet(userid,*posts)
                logger.info("FINISH USER:" + userid + " => " + str(len(posts)))

    def read_target_user(self,limit=50) -> list:
        try:
            self.db.connect()
            self.db.cursor.execute("SELECT user_id,sum(status) as sum From follower GROUP BY user_id having sum = 0 limit 1")
            root_userid = self.db.cursor.fetchall()[0][0]
            self.db.cursor.execute("SELECT follower_user_id From follower WHERE user_id = %s limit %s",[root_userid,limit])
            userids= [userid[0] for userid in self.db.cursor.fetchall()]
            self.db.cursor.execute(('UPDATE follower SET status=1 WHERE user_id = %s' % root_userid) + " and follower_user_id in (%s)" % ', '.join(list(map(lambda x: '%s', userids))),userids)            
            self.db.commit()
        except mydb.errors.ProgrammingError as e:
            traceback.print_exc()
            logger.debug(e)
            sys.exit()
        except Exception as e:
            traceback.print_exc()
            self.db.rollback()
            self.db.close()
            logger.error(e)
            sys.exit()
        self.db.close()

        return userids

    def insert_tweet(self,userid:int,*posts: list) -> None:
        self.db.connect()
        dup_entry = 0
        for post in posts:
            try:
                self.db.cursor.execute("INSERT INTO post (user_id,post_id,post) VALUES (%s,%s,%s)",[userid,post["id_str"],json.dumps(post)])
                self.db.commit()
            except mydb.errors.ProgrammingError as e:
                logger.debug(e)
                sys.exit()
            except mydb.errors.IntegrityError as e:
                if "Duplicate" in str(e) or "duplicate" in str(e):
                    dup_entry +=1
                    continue
                else:
                    logger.error(e)
                    sys.exit()
            except Exception as e:
                self.db.rollback()
                self.db.close()
                logger.error(e)
                sys.exit()
        self.db.close()
        logger.info("DUPLICATRE ENTRY:" + str(dup_entry))
        
    # @retry_api
    def fetch_post(self,user_id: str,limit: int=200) -> dict:
        try:
            posts =  [post._json for post in self._client.user_timeline(user_id = user_id,include_rts = True,exclude_replies=False,count=limit)]
        except tweepy.error.TweepError as e:
            return {"posts":[],"api_code":e.api_code}
        
        return {"posts":posts,"api_code":None}

class User(TwitterApi):
    follower_limit=cfg["user"]["GETTING_FOLLOWER_LIMIT"]
    def register_follower(self) -> str:
        '''
        fetch user from db & fetch follower from api & register follower on db.
        '''
        while True:
            time.sleep(3)
            userids = self.read_target_user()
            for userid in userids:
                t = self.fetch_follower(userid)
                followerids,api_code = t["followers"],t["api_code"]
                
                if len(followerids) == 0:
                    continue
                self.insert_follower(userid,*followerids)

    # def read_target_user(self,limit: int=10) -> list:
    def read_target_user(self,limit=10) -> list:
        self.db.connect()
        try:
            self.db.cursor.execute("SELECT user_id From user WHERE status = 0 LIMIT %s FOR UPDATE",[limit])
            userids = [userid[0] for userid in self.db.cursor.fetchall()]
            self.db.cursor.execute('UPDATE user SET status=1 WHERE user_id in (%s)'  % ', '.join(list(map(lambda x: '%s', userids))), userids)
            self.db.commit()
        except mydb.errors.ProgrammingError as e:
            traceback.print_exc()
            logger.debug(e)
            sys.exit()
        except Exception as e:
            traceback.print_exc()
            self.db.rollback()
            self.db.close()
            logger.error(e)
            sys.exit()
        self.db.close()

        return userids

    def insert_follower(self,userid:int,*followerid: str) -> None:
        self.db.connect()
        dup_entry = 0
        for followerid in followerid:
            print(followerid,userid)
            try:
                self.db.cursor.execute("INSERT INTO follower (user_id,follower_user_id) VALUES (%s,%s)",[userid,followerid])
                self.db.commit()
            except mydb.errors.ProgrammingError as e:
                logger.debug(e)
                sys.exit()
            except mydb.errors.IntegrityError as e:
                if "Duplicate" in str(e) or "duplicate" in str(e):
                    dup_entry +=1
                    continue
                else:
                    logger.error(e)
                    sys.exit()
            except Exception as e:
                self.db.rollback()
                self.db.close()
                logger.error(e)
                sys.exit()
        self.db.close()
        logger.info("DUPLICATRE ENTRY:" + str(dup_entry))

    # @retry_api
    def fetch_follower(self,user_id: str) -> dict:

        ## {followers:"list",api_code:"str"}
        try:
            ## followers_under_5000 = [followers for followers in tweepy.Cursor(self._client.followers_ids,id=user_id).items()]
            followers = self._client.followers_ids(id=user_id)

        except tweepy.error.TweepError as e:
            return {"followers":[],"api_code":e.api_code}
        
        return {"followers":followers,"api_code":None}
        
    def register_target_user(self,json_path):
        users = self._read_user_from_json_file(json_path)
        self._insert_user(*users)

    def _insert_user(self,*user_id: str) -> None:
        self.db.connect()
        dup_entry = 0
        for user_id in user_id:
            try:
                self.db.cursor.execute("INSERT INTO user (user_id) VALUES (%s)",[user_id])
                self.db.commit()
            except mydb.errors.ProgrammingError as e:
                logger.debug(e)
                sys.exit()
            except mydb.errors.IntegrityError as e:
                if "Duplicate" in str(e) or "duplicate" in str(e):
                    dup_entry +=1
                    continue
                else:
                    logger.error(e)
                    sys.exit()
            except Exception as e:
                self.db.rollback()
                self.db.close()
                logger.error(e)
                sys.exit()
        self.db.close()
        logger.info("DUPLICATRE ENTRY:" + str(dup_entry))

    def _read_user_from_json_file(self,path:str) -> dict:
        with open(path, 'r',encoding='utf-8') as read_file:
            re = json.load(read_file)
            logger.info("READ ALL TARGET USER:" + str(len(re)) + " USERS")
        return re

class QueueingManager():
    def __init__(self,conn) -> None:
        raise NotImplementedError
