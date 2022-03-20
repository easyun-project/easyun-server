# -*- coding: utf-8 -*-
"""
  @module:  Common Utils
  @desc:    存放各类公共组件
  @auth:    aleck
"""

import boto3
from datetime import date, datetime
from .models import Datacenter, Account


_RESOURCE_EC2 = None

def get_ec2_resource():
    global _RESOURCE_EC2
    if _RESOURCE_EC2 is None:
        _RESOURCE_EC2 = boto3.resource('ec2')
    return _RESOURCE_EC2


def gen_dc_tag(dc_name, type='flag'):
    '''生成dcName对应的tag标签'''
    if type == 'flag':
        flagTag = {"Key": "Flag", "Value": dc_name}
    elif type == 'filter':
        flagTag = {'Name': 'tag:Flag', 'Values': [dc_name]}
    return flagTag


def gen_hash_tag(dc_name, type='flag'):
    '''查询并生成dcName对应的tag标签'''
    thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
    flagHash = thisDC.get_hash()
    if type == 'flag':
        flagTag = {"Key": "Flag", "Value": flagHash}
    elif type == 'filter':
        flagTag = {'Name': 'tag:Flag', 'Values': [flagHash]}
    return flagTag


def query_dc_list():
    '''从本地数据库查询datacenter名单'''
    try:
        # dcList = Datacenter.query.with_entities(Datacenter.name).all()
        dcList = [dc.name for dc in Datacenter.query.all()]
        return dcList
    except Exception as ex:
        # return 'get datacenter list error.'
        return str(ex)


def query_dc_region(dc_name):
    '''通过dcName查询Region信息'''
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
        if thisDC is None: 
            raise ValueError('Datacenter not existed, kindly create it first!')
        return thisDC.region
    except Exception as ex:
        return str(ex)

def query_dc_vpc(dc_name):
    '''通过dcName查询VPC信息'''
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
        return thisDC.vpc_id
    except Exception as ex:
        return 'Datacenter not existed, kindly create it first!'


def set_boto3_region(dc_name):
    '''设置Boto3会话默认region,返回region name'''
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = thisDC.region )   
        return thisDC.region
    except Exception as ex:
        return 'Datacenter not existed, kindly create it first!'


def get_server_name(svr_id):
    '''通过instanceID 查询服务器 tag:Name '''
    resource_ec2 = get_ec2_resource()
    try:
        if svr_id == None:
            raise ValueError('svr_id is None')
        server = resource_ec2.Instance(svr_id)
        tagName = next((tag['Value'] for tag in server.tags if tag["Key"] == 'Name'), None)
        # nameTag = [tag['Value'] for tag in server.tags if tag['Key'] == 'Name']
        # svrName = nameTag[0] if len(nameTag) else None
        return tagName
    except Exception:
        return None


def get_subnet_type(subnet_id):
    '''判断subnet type是 public 还是 private'''
    # 偷个懒仅以名称判断，完整功能待实现
    resource_ec2 = get_ec2_resource()
    try:
        if subnet_id == None:
            raise ValueError('subnet_id is None')    
        thisSubnet = resource_ec2.Subnet(subnet_id)
        nameTag = next((tag['Value'] for tag in thisSubnet.tags if tag["Key"] == 'Name'), None)
        if nameTag.lower().startswith('pub'):
            subnetType = 'public'
        elif nameTag.lower().startswith('pri'):
            subnetType = 'private'
        else:
            subnetType = None
        return subnetType
    except Exception:
        return None


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
    