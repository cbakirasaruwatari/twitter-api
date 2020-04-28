#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import configparser

def _getprop(func):
    return sys._getframe(2).f_locals.get(func.__name__, None)

def getter(func):
    prop = _getprop(func)
    if prop is None:
        return property(func)
    return prop.getter(func)

def setter(func):
    prop = _getprop(func)
    if prop is None:
        return property(None, func)
    return prop.setter(func)

def deleter(func):
    prop = _getprop(func)
    if prop is None: 
        return property(None, None, func)
    return prop.setter(func)

# def jsonload(func):
#     def wrapper(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except :

#     return wrapper

def config(path):
    if os.path.isfile(path) is False:
        raise FileNotFoundError("設定ファイルがないよ")
    cfg = configparser.ConfigParser(os.environ)
    cfg.read(path)

    return cfg