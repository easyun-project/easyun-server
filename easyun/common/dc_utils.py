# -*- coding: utf-8 -*-
"""
  @module:  Datacenter Utils
  @desc:    Datacenter 相关公共工具（操作本地数据库模型，与云平台无关）
"""

from easyun.common.models import Datacenter


def gen_dc_tag(dc_name, type='flag'):
    '''生成dcName对应的tag标签'''
    if type == 'flag':
        return {"Key": "Flag", "Value": dc_name}
    elif type == 'filter':
        return {'Name': 'tag:Flag', 'Values': [dc_name]}


def gen_hash_tag(dc_name, type='flag'):
    '''查询并生成dcName对应的tag标签'''
    thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
    flagHash = thisDC.get_hash()
    if type == 'flag':
        return {"Key": "Flag", "Value": flagHash}
    elif type == 'filter':
        return {'Name': 'tag:Flag', 'Values': [flagHash]}


def query_dc_list():
    '''从本地数据库查询datacenter名单'''
    try:
        return [dc.name for dc in Datacenter.query.all()]
    except Exception as ex:
        return str(ex)


def query_dc_region(dc_name):
    '''通过dcName查询Region信息'''
    try:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
        if thisDC is None:
            raise ValueError('Datacenter not existed, kindly create it first!')
        return thisDC.region
    except Exception as ex:
        return str(ex)


def query_dc_vpc(dc_name):
    '''通过dcName查询VPC信息'''
    try:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
        return thisDC.vpc_id
    except Exception:
        return 'Datacenter not existed, kindly create it first!'


def set_boto3_region(dc_name):
    '''查询 datacenter 对应的 region name'''
    thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
    if thisDC:
        return thisDC.region
    else:
        raise ValueError(f'{dc_name} does not exist !')
