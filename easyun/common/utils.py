# -*- coding: utf-8 -*-
"""
  @module:  Common Utils
  @desc:    存放各类公共组件
  @auth:    aleck
"""

from datetime import date, datetime
from .models import Datacenter, Account


def query_region(dc):
    '''通过dcName查询Region信息'''
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dc).first()
        return thisDC.region
    except Exception as ex:
        return 'Datacenter not existed, kindly create it first!'


def len_iter(iterator):
    '''获取迭代器资源列表长度'''
    # 相比 len(list(iterator)) 方式消耗更少内存
    if hasattr(iterator,"__len__"):
        return len(iterator)
    else:
        return sum(1 for _ in iterator)


def json_datetime_serializer(obj):
    '''Helper method to serialize datetime fields'''
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))