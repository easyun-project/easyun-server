# -*- coding: utf-8 -*-
"""
  @module:  DataCenter: Gateway
  @desc:    Datacenter gateway management, including Internet Gateway and NAT Gateway
  @auth:    aleck
"""

import boto3
from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from . import bp


@bp.get('/igw')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_igw_detail(param):
    '''获取全部Internet网关(IGW)信息 [Mock]'''
    pass

    igwList = [
        {
            'tagName': 'easyun-igw',
            'igwId': 'igw-0ac4fceed4468d269',
            'vpcId': 'vpc-0cb099babd31f03d1',
            'vpcName': 'VPC-Easyun1',
            'igwState': 'attached',
            'userTags': [{'Key': 'Env', 'Value': 'development'}],
        },
    ]

    response = Result(detail=igwList, status_code=200)
    return response.make_resp()


@bp.get('/natgw')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_natgw_detail(param):
    '''获取全部NAT网关(NAT GW)信息 [Mock]'''

    natgwList = [
        {
            'tagName': 'easyun-natgw',
            'natgwId': 'nat-06f2da484710f7da0',
            'vpcId': 'vpc-057f0e3d715c24147',
            'vpcName': 'VPC-Easyun',
            'natgwState': 'available',
            'connType': 'Public',
            'subnetId': 'subnet-06bfe659f6ecc2eed',
            'pubIp': '3.229.72.25',
            'priIp': '10.11.1.32',
            'userTags': [{'Key': 'Env', 'Value': 'demo'}],
        },
    ]

    response = Result(detail=natgwList, status_code=200)
    return response.make_resp()
