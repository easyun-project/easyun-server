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
def get_account_quota():
    '''获取云账号下资源配额 [mock]'''
    pass
    resp = Result(
        detail = '功能开发中...',
        status_code=200
    )
    return resp.make_resp()


@bp.get('/quota/<region>')
@auth_required(auth_token)
# @input(DcNameQuery, location='query')
def get_region_quota(region):
    '''获取指定region的资源配额 [mock]'''

    AWS_Valid_Quota = [
            {
                'qoutaName':'od_instances',
                'serviceCode':'ec2',
                'quotaCode':'L-1216C47A',
                'quotaDes' :'Running On-Demand Standard (A, C, D, H, I, M, R, T, Z) instances'
            },
            {
                'qoutaName':'spot_instances',
                'serviceCode':'ec2',
                'quotaCode':'L-34B43A08',
                'quotaDes' :'All Standard (A, C, D, H, I, M, R, T, Z) Spot Instance Requests'
            },
            {
                'qoutaName':'eips',
                'serviceCode':'ec2',
                'quotaCode':'L-0263D0A3',
                'quotaDes' :'EC2-VPC Elastic IPs'
            },            
    ]

    client_sq = boto3.client('service-quotas', region_name= region)

    eipQuota = client_sq.get_service_quota(
            ServiceCode='ec2',
            QuotaCode='L-0263D0A3'  #EC2-VPC Elastic IPs
    #             QuotaCode='L-1216C47A'  #Running On-Demand Standard
    )['Quota']

    quotaList = []
    vpcLimit = {
            'vpcQuota' : 5,
            'eipQuota' : eipQuota.get('Value'),
            'natQuota' : 5,
            'igwQuota': 10,
            'eniQuota': 10,
            'secgroupQuota' : 5,
            'subnetQuota': 200
            }
    quotaList.append(vpcLimit)
        
    resp = Result(
        detail = quotaList,
        status_code=200
    )
    return resp.make_resp()