# -*- coding: utf-8 -*-
"""
  @module:  Easyun Libs Utils
  @desc:    存放Easyun基础性公共组件
  @auth:    aleck
"""
import os
import json
from collections import Counter
from datetime import date, datetime


def load_json_config(file, location = 'easyun/config'):
    '''load config from json file'''
    file_name = '%s.%s' %(file,'json')
    with open(os.path.join(location, file_name), encoding='utf-8') as f:
        config = json.load(f).get('config')
    return config


def filter_list_by_key(full_list:list,key:str):
    '''过滤列表:按指定字段筛选'''
    filtedList = [i.get(key) for i in full_list]
    return filtedList


def filter_list_by_value(full_list:list,key:str,value:str):
    '''过滤列表:按指定字段取值筛选'''
    filtedList = [i for i in full_list if i.get(key) == value]
    return {
        'countNum':len(filtedList),
        'countList':filtedList
    }


def len_iter(iterator):
    '''获取迭代器(Colleciton)列表长度'''
    # 相比 len(list(iterator)) 方式消耗更少内存
    if hasattr(iterator,"__len__"):
        return len(iterator)
    else:
        return sum(1 for _ in iterator)


def datetime_serializer(obj):
    '''Helper method to serialize datetime fields'''
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
    