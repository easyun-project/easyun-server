# -*- coding: utf-8 -*-
"""
  @author:  pengchang
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited. 
  @file:    datacenter_default.py
  @desc:    The DataCenter default module
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, DC_REGION, TagEasyun
from flask import jsonify


DefaultParm = {
    'region': DC_REGION, #默认跟Easyun部署Region一致
    'az_list' : ['us-east-1a','us-east-1b'],
    'vpc_cidr' : '10.10.0.0/16',
    'pub_subnet1' : '10.10.1.0/24',
    'pub_subnet2' : '10.10.2.0/24',
    'pri_subnet1' : '10.10.3.0/24',
    'pri_subnet2' : '10.10.4.0/24',
    'secure_group1' : 'easyun-sg-default',
    'secure_group2' : 'easyun-sg-webapp',
    'secure_group3' : 'easyun-sg-database',
    'keypair' : "key_easyun_user",
    'tag_spec' : [{ "ResourceType":"instance","Tags": TagEasyun}]
}


class DataCenterListIn(Schema):
    vpc_id = String()


class ParmOut(Schema):
    region = String()
    az_list = List(String())
    vpc_cidr = String()
    pub_subnet1 = String()
    pub_subnet2 = String()
    pri_subnet1 = String()
    pri_subnet2 = String()
    secure_group1 = String() 
    secure_group2 = String() 
    secure_group3 = String()
    keypair = String()
    # category = String()
    tag_spec = List(Dict())


@bp.get('/default')
@auth_required(auth_token)
@output(ParmOut, description='Get DataCenter Info')
def default_parm():
    '''获取云数据中心默认创建参数'''
    RESOURCE = boto3.resource('ec2', region_name=DC_REGION)
    ec2 = boto3.client('ec2', region_name=DC_REGION)
    
    # vpcs = ec2.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': [FLAG]}])

    response = Result(
            detail = DefaultParm,
            status_code=2001
        )

    return response.make_resp()
    # return jsonify(NewDataCenter) 
