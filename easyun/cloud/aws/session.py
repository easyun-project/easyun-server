# -*- coding: utf-8 -*-
"""
  @module:  AWSCloud SDK Session
  @desc:    AWS Boto3 Session for Easyun SDK.
  @auth:    aleck
"""

import boto3
from easyun.common.models import Datacenter


def get_easyun_session(dc_name=None):
    '''创建 Boto3 Session，按 datacenter 名称自动设置 region'''
    if dc_name is None:
        return boto3.session.Session()

    thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
    if thisDC:
        return boto3.session.Session(region_name=thisDC.region)
    else:
        raise ValueError(f'{dc_name} does not exist !')


def get_easyun_client(service, dc_name=None, region_name=None):
    '''创建 boto3 client，优先用 dc_name 查 region，其次用 region_name'''
    if dc_name:
        session = get_easyun_session(dc_name)
    elif region_name:
        session = boto3.session.Session(region_name=region_name)
    else:
        session = boto3.session.Session()
    return session.client(service)


def get_easyun_resource(service, dc_name=None, region_name=None):
    '''创建 boto3 resource，优先用 dc_name 查 region，其次用 region_name'''
    if dc_name:
        session = get_easyun_session(dc_name)
    elif region_name:
        session = boto3.session.Session(region_name=region_name)
    else:
        session = boto3.session.Session()
    return session.resource(service)
