#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import json
# import ConfigParser
import traceback
import argparse

sys.path.append('../')
from base import twitterapi 

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def main():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial", type=str,required=False)
    args = parser.parse_args()

    ta = twitterapi.User()
    if args.initial == "true":
        if ta.register_target_user("../resource/target_users_twitter.json") == False:
            logger.error("Can't exec user registration")
            sys.exit()
    
    ta.register_follower()
    

    
                
    


