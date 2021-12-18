# -*- coding: utf-8 -*-
"""
  @file:    datacenter_default.py
  @desc:    DataCenter Default Value Module
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, REGION, FLAG, TagEasyun
from flask import jsonify
from  .datacenter_sdk import datacentersdk
from .schemas import DataCenterListOut

NewDataCenter = {
    'region': 'us-east-1',
    'az' : 'us-east-1a',
    'vpc_cidr' : '10.10.0.0/16',
    'pub_subnet1' : '10.10.1.0/24',
    'pub_subnet2' : '10.10.2.0/24',
    'pri_subnet1' : '10.10.3.0/24',
    'pri_subnet2' : '10.10.4.0/24',
    'secure_group1' : 'easyun-sg-default',
    'secure_group2' : 'easyun-sg-webapp',
    'secure_group3' : 'easyun-sg-database',
    'key' : "key_easyun_dev",
    'tag_spec' : [{ "ResourceType":"instance","Tags": TagEasyun}]
}


@bp.get('/default')
#@auth_required(auth_token)
# @app_log('get default info of data center')
@output(DataCenterListOut, description='Get DataCenter Info')
def get_datacentercfg():
    '''获取创建云数据中心默认参数'''
    RESOURCE = boto3.resource('ec2', region_name=REGION)
    ec2 = boto3.client('ec2', region_name=REGION)
    
    # vpcs = ec2.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': [FLAG]}])
    response = Result(detail=NewDataCenter, status_code=2001)
    return response.make_resp()
