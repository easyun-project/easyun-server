# -*- coding: utf-8 -*-
"""
  @module:  Dashboard Inventory
  @desc:    DataCenter resource inventory, including: server,storage,rds,networking,etc.
  @auth:    
"""

import boto3
from apiflask import Schema, input, output, auth_required
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import len_iter
from easyun.cloud.aws_region import AWS_Regions, query_country_code, query_region_name
from . import bp


@bp.get("/summary/datacenter")
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def summary_dc(parm):
    '''获取数据中心 Summary信息'''
    thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
    dcRegion = thisDC.get_region()
    # dcVPC = thisDC.get_vpc()

    regionDict = [region for region in AWS_Regions if region['regionCode']==dcRegion][0]
    regionInfo = {
        "icon" : regionDict.get('countryCode'),
        "name" : regionDict.get('regionName')['eng']
    }

    client_ec2 = boto3.client('ec2', region_name= dcRegion)
    azs = client_ec2.describe_availability_zones()

    summaryList = []
    for az in azs['AvailabilityZones']:
        azName = az.get('ZoneName')
    
        subnetResp = client_ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Flag',
                    'Values': [
                        parm['dc'],
                    ]
                },
                {
                    'Name':'availability-zone',
                    'Values': [
                        azName
                    ]
                }
            ],
        )
        subnetNum = len(subnetResp.get('Subnets'))
        azStatus = 'running' if subnetNum else 'empty'
        
        azItem = {
            "azName": azName,
            "azStatus": azStatus,
            "subnetNum": subnetNum,
            "dcRegion": regionInfo
        }
        summaryList.append(azItem) 

    resp = Result(
        detail = summaryList
        )
    return resp.make_resp()   


SUMMARY_TABLE = {
    'summary' : 'easyun-inventory-summary',
}