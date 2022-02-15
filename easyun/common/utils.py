# -*- coding: utf-8 -*-
"""
  @module:  Common Utils
  @desc:    存放各类公共组件
  @auth:    aleck
"""

import boto3
from datetime import date, datetime
from .models import Datacenter, Account


def query_dc_list():
    '''从本地数据库查询datacenter名单'''
    try:
        # dcList = Datacenter.query.with_entities(Datacenter.name).all()
        dcList = [dc.name for dc in Datacenter.query.all()]
        return dcList
    except Exception as ex:
        # return 'get datacenter list error.'
        return str(ex)


def query_dc_region(dc):
    '''通过dcName查询Region信息'''
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dc).first()
        return thisDC.region
    except Exception as ex:
        return 'Datacenter not existed, kindly create it first!'

   
def query_svr_name(svr_id):
    '''通过instanceID 查询服务器 tag:Name '''
    resource_ec2 = boto3.resource('ec2')
    server = resource_ec2.Instance(svr_id)
    nameTag = next((tag['Value'] for tag in server.tags if tag["Key"] == 'Name'), None)
    # nameTag = [tag['Value'] for tag in server.tags if tag['Key'] == 'Name']
    # svrName = nameTag[0] if len(nameTag) else None
    return nameTag


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