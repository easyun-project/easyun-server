# -*- coding: utf-8 -*-
"""
  @module:  AWSCloud SDK Session
  @desc:    AWS Boto3 Session for Easyun SDK.
  @auth:    aleck
"""

import boto3
from easyun.common.models import Datacenter


_EASYUN_SESSION = boto3.session.Session()


def get_easyun_session(dc_name=None):
    '''设置Boto3 Session 默认region,返回region name'''
    global _EASYUN_SESSION
    # return current session if no dc_name is specified
    if dc_name is None:
        return _EASYUN_SESSION
    else:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
    if thisDC:
        dcRegion = thisDC.region
        # Get or Create Easyun boto3 session
        if _EASYUN_SESSION is not None and _EASYUN_SESSION.region_name == dcRegion:
            return _EASYUN_SESSION
        else:
            _EASYUN_SESSION = boto3.session.Session(region_name=dcRegion)
            return _EASYUN_SESSION
    else:
        raise ValueError(f'{dc_name} does not exist !')
