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
