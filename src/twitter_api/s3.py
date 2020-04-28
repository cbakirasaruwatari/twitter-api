#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import configparser
import boto3
from boto3.session import Session
import json
from datetime import datetime


class S3:
  _CFG_PATH:str = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource/settings/aws.cfg'))
  cfg = configparser.ConfigParser(os.environ)
  cfg.read(_CFG_PATH)
  arn=cfg["credential"]["arn"]
  client = boto3.client('sts')
  response =  client.assume_role(
              RoleArn=arn,
              RoleSessionName="temp"
          )
  session = Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                  aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                  aws_session_token=response['Credentials']['SessionToken'],
                  region_name='ap-northeast-1')

  def __init__(self):
    pass

  def reflesh(self):
    self.client = boto3.client('sts')
    self.response = self.client.assume_role(
              RoleArn=self.arn,
              RoleSessionName="temp"
          )
    
    self.session = Session(aws_access_key_id=self.response['Credentials']['AccessKeyId'],
      aws_secret_access_key=self.response['Credentials']['SecretAccessKey'],
      aws_session_token=self.response['Credentials']['SessionToken'],
      region_name='ap-northeast-1')
    
  def request(self,file_path,s3path:str):
    try:
      self.session.resource('s3').Bucket('twitter-account').upload_file(file_path,s3path)
    except boto3.exceptions.S3UploadFailedError:
      self.reflesh()
      self.session.resource('s3').Bucket('twitter-account').upload_file(file_path,s3path)

  # del transffered file.
    # os.remove(file_path)

