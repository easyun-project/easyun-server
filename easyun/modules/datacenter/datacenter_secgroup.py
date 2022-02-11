# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from flask import request
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp,DryRun
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from .schemas import DataCenterEIPIn,DataCenterNewEIPIn,DataCenterListsIn,DataCenterListIn,DcParmIn,DataCenterSubnetIn



@bp.get('/secgroup')
#@auth_required(auth_token)
@input(DataCenterListIn, location='query')
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def list_secgroup(param):
    dc_name=param['vpc_id']
    type=param['seurityid']
    '''获取数据中心全部SecurityGroup [mock]'''
    sgList = [
        {
            "tagName": "easyun-sg-default",
            'sgId': 'sg-0a818f9a74c0657ad',
            'sgDes': 'default VPC security group',
            'ipPermissions': [
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [
                        {'CidrIp': '0.0.0.0/0'}
                    ],
                },           
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3389,
                    'ToPort': 3389,
                    'IpRanges': [{
                        'CidrIp': '0.0.0.0/0'
                    }]
                }
            ]
        },
        {
            "tagName": "easyun-sg-webapp",
            'sgId': 'sg-02f0f5390e1cba746',
            'sgDes': 'allow web application access',
            'ipPermissions': [
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [
                        {'CidrIp': '0.0.0.0/0'}
                    ],
                },           
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{
                        'CidrIp': '0.0.0.0/0'
                    }]
                }
            ]            
        },
        {
            "tagName": "easyun-sg-database",
            'sgId': 'sg-05df5c8e8396d06e9',
            'sgDes': 'allow database access',
            'ipPermissions': [
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [
                        {'CidrIp': '0.0.0.0/0'}
                    ],
                },           
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3389,
                    'ToPort': 3389,
                    'IpRanges': [{
                        'CidrIp': '0.0.0.0/0'
                    }]
                }
            ] 
        }
    ]

    TagEasyunSecurityGroup= [ 
        {'ResourceType':'security-group', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": 'securitygroup[name]'}
            ]
        }
    ]

    resp = Result(
        detail = sgList,
        status_code=200
    )
    return resp.make_resp()



@bp.delete('/secgroup')
@auth_required(auth_token)
@input(DcParmIn)
def delete_secgroup(param):
    '''删除 SecurityGroup [mock]'''   
    resp = Result(
        detail = {
            'secgroupId':'sg-xxxxxxx'
        },
        status_code = 200 
    )

    return resp.make_resp()