# -*- coding: utf-8 -*-
"""
  @module:  Account Qoutas
  @desc:    获取云账号下资源配额相关信息
  @auth:    aleck
"""


import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp



@bp.get('/quota')
@auth_required(auth_token)
# @input(DcNameQuery, location='query')
def get_cloud_quota(param):
    '''获取云账号下资源配额 [mock]'''
    dcName=param.get('dcName')
    
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    if (thisDC is None):
            response = Result(message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
            response.err_resp() 
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    resource_ec2 = boto3.resource('ec2', region_name= thisDC.region)
    vpc = resource_ec2.Vpc(thisDC.vpc_id)
    noVPCUsed = len(list(resource_ec2.vpcs.all()))
    noSecurityGroupUsed = len(list(resource_ec2.security_groups.all()))
    noSubnetsUsed = len(list(resource_ec2.subnets.all()))
    noEIPUsed = len(list(resource_ec2.vpc_addresses.all()))
    noIGUsed = len(list(resource_ec2.internet_gateways.all()))
    noNetworkInterfaceUsed = len(list(resource_ec2.network_interfaces.all()))


    qoutaList = []
    vpcLimit = {
            'vpc limit' : 5,
            'EIP limit' : 5,
            'NAT limit' : 5,
            'Internet Gateway Limit': 10,
            'Network Interface Limit': 10,
            'Security Group Limit' : 5,
            'Subnet Limit': 200
            }

    qoutaList.append(vpcLimit)

        
    resp = Result(
        detail = qoutaList,
        status_code=200
    )
    return resp.make_resp()