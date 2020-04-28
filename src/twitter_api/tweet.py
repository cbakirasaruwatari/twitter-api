#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
import json
from pathlib import Path
import math
# import ConfigParser
import traceback
import argparse

from typing import Any

from api_base import APIMeta

class APITweet(APIMeta):
    methods:list=["lookup_users","user_timeline","retweeters","retweets"]

    def __init__(self,method,*,destination: Any,resource: Any):
        if method not in self.methods:
            raise NotImplementedError
        super(APITweet, self).__init__(method,resource,destination)

    def start(self):
        targets = self.fetch_target()
        for v in targets:
            response = self.acsr.do_method(cursor=True,id=v)
            self.rpcr.save(user.resource.stem + "/" + str(v),*[response])


    def start_ids(self,id_name,chunksize):
        targets = self.fetch_target()
        chunk_size = math.ceil(len(targets) / chunksize)
        result = []

        for i in range(chunk_size):
            response = self.acsr.do_method(id_name=targets[i:i+chunksize])
            result.append(response)
        self.rpcr.save(str(self.resource.stem),*result)


    def start_id(self,id_name):
        targets = self.fetch_target()
        for v in targets:
            response = self.acsr.do_method(cursor=True,id_name=v)
            self.rpcr.save(str(self.resource.stem),*[response])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Make wow!') 
    parser.add_argument('method')
    parser.add_argument('resource')

    args = parser.parse_args()
    path = "resource/" + args.resource
    files = os.listdir(path)
    files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
    
    for file in files_file:
        user = APITweet(args.method, destination=Path(''),resource=Path(path + "/" + file))
        print("start")
        user.start()
        print("finish")