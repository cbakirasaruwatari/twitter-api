#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import json
from pathlib import Path
# import ConfigParser
import traceback
import argparse

from typing import Any

from api_base import APIMeta

import math
import os

class APIUser(APIMeta):
    methods:list=["followers_ids"]

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

    path = "temp_followers_ids"
    files = os.listdir(path)
    files_file = [f for f in files if os.path.isfile(os.path.join(path, f))][1:]

    
    for file in files_file:

        user = APIUser("followers_ids", destination=Path(''),resource=Path(path + "/" + file))
        print("start")
        user.start()
        print("finish")







