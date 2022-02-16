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
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.utils import len_iter, query_dc_region
from easyun.common.schemas import DcNameQuery
from . import bp,DryRun
from .schemas import DataCenterEIPIn,DataCenterNewEIPIn,DataCenterListsIn,DataCenterListIn,DcParmIn,DataCenterSubnetIn



@bp.get('/secgroup')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def list_secgroup_detail(parm):
    '''获取数据中心全部SecurityGroup信息'''    
    dcName=parm['dc']
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )
        client_ec2 = boto3.client('ec2')

        sgs = client_ec2.describe_security_groups(
            Filters=[
                {
                    'Name': 'tag:Flag', 'Values': [dcName]
                },             
            ]
        )['SecurityGroups']

        sgList = []
        for sg in sgs:
            # 获取Tag:Name
            nameTag = next((tag['Value'] for tag in sg.get('Tags') if tag["Key"] == 'Name'), None)            
            sgItem = {
                'sgId':sg['GroupId'],
                'tagName': nameTag,
                'sgName': sg['GroupName'],                
                'sgDes':sg['Description'],
                # Inbound Ip Permissions
                'ibrulesNum':len(sg['IpPermissions']),                
                'ibPermissions':sg['IpPermissions'],
                # Outbound Ip Permissions
                'obrulesNum':len(sg['IpPermissionsEgress']),                
                'obPermissions':sg['IpPermissionsEgress'] 
            }
            sgList.append(sgItem)    

        resp = Result(
            detail = sgList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            detail=str(ex), 
            status_code=2030
        )
        resp.err_resp()



@bp.get('/secgroup/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def list_secgroup_brief(parm):
    '''获取 全部SecurityGroup列表[仅基础字段]'''
    dcName=parm['dc']
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )
        client_ec2 = boto3.client('ec2')

        sgs = client_ec2.describe_security_groups(
            Filters=[
                {
                    'Name': 'tag:Flag', 'Values': [dcName]
                },             
            ]
        )['SecurityGroups']

        sgList = []
        for sg in sgs:
            # 获取Tag:Name
            nameTag = next((tag['Value'] for tag in sg.get('Tags') if tag["Key"] == 'Name'), None)            
            sgItem = {
                'sgId':sg['GroupId'],
                'tagName': nameTag,
                'sgName': sg['GroupName'],                
                'sgDes':sg['Description'],
            }
            sgList.append(sgItem)    

        resp = Result(
            detail = sgList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            detail=str(ex), 
            status_code=2030
        )
        resp.err_resp()



@bp.delete('/secgroup')
@auth_required(auth_token)
@input(DcParmIn)
def delete_secgroup(param):
    '''删除 SecurityGroup 【mock】'''   
    resp = Result(
        detail = {
            'secgroupId':'sg-xxxxxxx'
        },
        status_code = 200 
    )

    return resp.make_resp()


TagEasyunSecurityGroup= [ 
    {'ResourceType':'security-group', 
        "Tags": [
        {"Key": "Flag", "Value": "Easyun"},
        {"Key": "Name", "Value": 'securitygroup[name]'}
        ]
    }
]