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

    ta = twitterapi.Tweet()
    ta.register_tweet()
    