#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import datetime
import json
import pathlib
import logging
import time
import traceback
import configparser
# from functools import partial
from abc import ABCMeta,abstractmethod
from dataclasses import dataclass,asdict
import itertools
from typing import Optional,Union,NewType,Tuple, List, Any, Dict, Callable, Generic, NoReturn
from typing import overload

import mysql.connector as mydb
import tweepy
import boto3

from db import PersitenceDatabase
from s3 import S3
from util import getter,setter,config

_RESOURCE_PATH_API='resource/settings/api.cfg'

DATE = datetime.datetime.now()

@dataclass
class ApiResponse:
    body:Union[Dict,List]
    api_code: Optional[str]
    date: str
    version: str


class APIMeta(metaclass = ABCMeta):

    class APIAccessor:

        _CFG_PATH:str = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), _RESOURCE_PATH_API))
        def __init__(self,method_name) -> NoReturn:
            cfg = config(self._CFG_PATH)
            auth = tweepy.OAuthHandler(cfg["auth"]["consumer_key"],cfg["auth"]["consumer_secret"])
            auth.set_access_token(cfg["auth"]["access_token"],cfg["auth"]["access_token_secret"])
            self.client = tweepy.API(auth,wait_on_rate_limit = True)
            self.method:Callable = getattr(self.client,method_name)
        @getter
        def method(self) -> Callable:
            return self._method
        @setter
        def method(self,func:Callable) -> NoReturn:
            if (func.__module__) == "tweepy.binder" or hasattr(tweepy.api,func.__name__):
                self._method = func
            else:
                raise TypeError("method value is ...MAKE WOW!:b")

        def do_method(self,cursor:bool=False,**q:str):
            try:
                if cursor is False:
                    body = [self.method(**q)]
                else:
                    body = [response for response in tweepy.Cursor(self.method, **q).items()]
                result = ApiResponse(
                    body=body,
                    api_code=None,
                    date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    version=0
                )
            except tweepy.error.TweepError as e:
                result = ApiResponse(
                    body=[],
                    api_code=e.api_code,
                    date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    version=0
                )
            return result

    class ResultProcesser:

        def __init__(self,method_name:str,s3):
            self.method_name=method_name
            # self.db = db
            self.s3 = s3
        
        def save(self,name:str,*responses:ApiResponse):
            data = [asdict(response) for response in responses]
            path = self.__save_as_buffer(data[0],name +  ".json")
            name = path.name.replace("_","/")
            self.__save_to_s3(path,self.method_name + "/" + "Year=" + str(DATE.year) + "/Month=" + str(DATE.month) + str("/Day=") + str(DATE.day) + "/" + name)
        
        def __save_as_buffer(self,data:dict,name:str) -> pathlib.Path:
            if not os.path.exists("temp_" + self.method_name):
                os.mkdir("temp_" + self.method_name)
            name_replaced = name.replace("/","_")
            with open("temp_" + self.method_name + "/" + name_replaced, 'w') as f:
                # data["date"] = data["date"].strftime('%Y-%m-%d %H:%M:%S')
                json.dump(data, f, ensure_ascii=False)
            return pathlib.Path("temp_" + self.method_name + "/" + name_replaced)
            
        def __save_to_s3(self,path:pathlib.Path,s3path:str):
            self.s3.request(str(path),s3path)
            
        def __save_to_db(self):
            raise NotImplementedError

    def __init__(self,method_name: str,resource: str,destination: str) -> NoReturn:

        self.resource: Union[pathlib.Path,PersitenceDatabase.Model.Base] = resource
        self.destination: Union[pathlib.Path,PersitenceDatabase.Model.Base] = destination

        if isinstance(self.destination,PersitenceDatabase.Model.Base) or isinstance(self.resource,PersitenceDatabase.Model.Base):
            self.db = PersitenceDatabase("twitter2")
            # self.s3 = S3()
        
        self.acsr = self.APIAccessor(method_name)
        self.rpcr = self.ResultProcesser(method_name,S3())

    @getter
    def destination(self) -> Union[pathlib.Path,PersitenceDatabase.Model.Base]:
        return self._detination 
    @setter
    def destination(self, dst:Union[pathlib.Path,PersitenceDatabase.Model.Base]) -> NoReturn:
        if  isinstance(dst,pathlib.Path) or isinstance(dst,PersitenceDatabase.Model.Base):
            self._detination = dst
        else:
            raise TypeError("dest value is ...MAKE WOW!")

    @getter
    def resource(self) -> Union[pathlib.Path,PersitenceDatabase.Model.Base]:
        return self._resource
    @setter
    def resource(self, rsc:Union[pathlib.Path,PersitenceDatabase.Model.Base]) -> NoReturn:
        if  isinstance(rsc,pathlib.Path) or isinstance(rsc,PersitenceDatabase.Model.Base):
            self._resource = rsc
        else:
            raise TypeError("rsc value is ...MAKE WOW!")

    @abstractmethod
    def start(self,resource_column:str=None):
        raise NotImplementedError
        # for v in self.fetch_target():
        #     response = self.acsr.do_method(id=v)
        #     self.rpcr.save(response,v)
   
    def fetch_target(self,column:str=None) -> list:
        if issubclass(type(self.resource),pathlib.Path):
            return self.__fetch_target_from_file(str(self.resource))

        elif issubclass(self.resource, PersitenceDatabase.Model.Base):
            return self.__fetch_target_from_db(self.resource,column)

    def __fetch_target_from_file(self,path: str):
        if os.path.exists(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))):
            with open(path) as f:
                return json.load(f)
        else:
            raise ValueError()
    
    def __fetch_target_from_db(self, model, column:str):
        if column == None:
            return [ v[column] for v in self.db.fetch_all(model)]
        else:
            return [ v[column] for v in self.db.fetch_all(model,column)]


    # @abstractmethod
    # def start(self):
    #     raise NotImplementedError