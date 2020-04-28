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

class APIUser(APIMeta):
    methods:list=["followers_ids","lookup_users"]

    def __init__(self,method,*,destination: Any,resource: Any):
        if method not in self.methods:
            raise NotImplementedError
        super(APIUser, self).__init__(method,resource,destination)

    def start(self):
        targets = self.fetch_target()["body"]
        chunk_size = math.ceil(len(targets) / 100)
        result = []

        for i in range(chunk_size):
            response = self.acsr.do_method(user_ids=targets[i:i+100])
            result.append(response)
        self.rpcr.save(str(self.resource.stem),*result)

if __name__ == "__main__":
    # follower = APIUser("followers_ids", destination=Path(''),resource=Path("resource/target_users_twitter.json"))
    # follower.start()

    path = "temp_followers_ids"
    files = os.listdir(path)
    files_file = [f for f in files if os.path.isfile(os.path.join(path, f))][1:]

    
    for file in files_file:

        user = APIUser("lookup_users", destination=Path(''),resource=Path(path + "/" + file))
        print("start")
        user.start()
        print("finish")
