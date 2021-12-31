# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter


@bp.get('/azone/<dc_name>')
@auth_required(auth_token)
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_azones(dc_name):
    '''获取数据中心 Availability Zone 列表'''
    # only for globa regions
    thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)
    azs = client_ec2.describe_availability_zones()
    azList = [az['ZoneName'] for az in azs['AvailabilityZones']] 

    resp = Result(
        detail = azList,
        status_code=200
    )
    return resp.make_resp()


@bp.get('/subnet/<dc_name>')
@auth_required(auth_token)
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_subnets(dc_name):
    '''获取数据中心现有资源: Subnet [mock]'''
    pubSubnet1 = {
        "tagName": "Public subnet 1",
        'subnetId':'subnet-06bfe659f6ecc2eed',
        'subnetType': 'public',
        "cidr": "10.10.1.0/24",
        "az": "us-east-1a",
        'freeIps': 249
    }
    pubSubnet2 = {
        "tagName": "Public subnet 2",
        'subnetId':'subnet-02a09fd044f6d8e8d',
        'subnetType': 'public',
        "cidr": "10.10.2.0/24",
        "az": "us-east-1b",
        'freeIps': 247
    }
    priSubnet1 = {
        "tagName": "Private subnet 1",
        'subnetId':'subnet-03c3de7f09dfe36d7',
        'subnetType': 'private',
        "cidr": "10.10.21.0/24",
        "az": "us-east-1a",
        'freeIps': 251
    }
    priSubnet2 = {
        "tagName": "Private subnet 2",
        'subnetId':'subnet-0c903785974d075f0',
        'subnetType': 'private',
        "cidr": "10.10.22.0/24",
        "az": "us-east-1b",
        'freeIps': 244
    }


    resp = Result(
        detail = [pubSubnet1,pubSubnet2,priSubnet1,priSubnet2],
        status_code=200
    )
    return resp.make_resp()

@bp.get('/secgroup/<dc_name>')
@auth_required(auth_token)
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def list_secgroups(dc_name):
    '''获取数据中心现有资源: SecurityGroup [mock]'''
    sgList = [
        {
            "tagName": "easyun-sg-default",
            'sgId': 'sg-0a818f9a74c0657ad',
            'sgDes': 'default VPC security group'
        },
        {
            "tagName": "easyun-sg-webapp",
            'sgId': 'sg-02f0f5390e1cba746',
            'sgDes': 'allow web application access'
        },
        {
            "tagName": "easyun-sg-database",
            'sgId': 'sg-05df5c8e8396d06e9',
            'sgDes': 'allow database access'
        }
    ]

    resp = Result(
        detail = sgList,
        status_code=200
    )
    return resp.make_resp()