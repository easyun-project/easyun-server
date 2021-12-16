# -*- coding: utf-8 -*-
"""
  @author:  pengchang
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited. 
  @file:    datacenter_get.py
  @desc:    The DataCenter Get module
"""
# from _typeshed import NoneType
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Account,Datacenter
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, REGION, FLAG
from flask import jsonify
from  .datacenter_sdk import datacentersdk


NewDataCenter = {
    'region': 'us-east-1',
    'vpc_cidr' : '10.10.0.0/16',
    'avaibility_zone' : 'us-east-1a',
    'pub_subnet1' : '10.10.1.0/24',
    'pub_subnet2' : '10.10.2.0/24',
    'pri_subnet1' : '10.10.3.0/24',
    'pri_subnet2' : '10.10.4.0/24',
    'key' : "key_easyun_dev",
    'secure_group1' : 'easyun-sg-default',
    'secure_group2' : 'easyun-sg-webapp',
    'secure_group3' : 'easyun-sg-database',
    'tag_spec' : [
        {
        "ResourceType":"instance",
        "Tags": [
                {"Key": "Flag", "Value": FLAG},
                {"Key": "Name", "Value": 'test-from-api'}
            ]
        }
        ]
}


class DataCenterListIn(Schema):
    vpc_id = String()


class DataCenterListOut(Schema):
    region_name = String()
    vpc_id = String()
    azs = List(String)
    subnets = List(String)
    securitygroup = List(String)
    keypair = List(String)
    create_date = String()
    

@bp.get('/all')
#@auth_required(auth_token)
@output(DataCenterListOut, description='Get DataCenter Region Info')
def get_datacenter_all():
    '''获取Easyun环境下云数据中心信息'''
    RESOURCE = boto3.resource('ec2', region_name=REGION)
    ec2 = boto3.client('ec2', region_name=REGION)

    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': [FLAG]}])

    # vpcs = client1.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': [FLAG]}])

#    datacenters = Datacenter.query.filter_by(id=2).first()
    datacenters:Datacenter  = Datacenter.query.filter_by(id=1).first()
    # datacenters:Datacenter  = Datacenter.query.get(1)

    # datacenters = Datacenter.query.first()
    # if len(datacenters) == 0:
    # if (datacenters.count()  == 0):
    if (datacenters is None):
        response = Result(detail ={'Result' : 'Errors'}, message='No Datacenter available, kindly create it first!', status_code=3001,http_status_code=400)
        print(response.err_resp())
        response.err_resp()   
    else:
        vpc_id=datacenters.vpc_id
        region_name=datacenters.region
        create_date =datacenters.create_date
    
    # print(vpc_id)
    # print(datacenters.id)


    # regions = ec2.describe_regions(Filters=[{'Name': 'region-name','Values': [REGION]}])

    az_list = ec2.describe_availability_zones(Filters=[{'Name': 'group-name','Values': [REGION]}])

    az_ids = [ az['ZoneName'] for az in az_list['AvailabilityZones'] ]

#    list1=[]
    # for i in range(len(az_list['AvailabilityZones'])):
    # for i, azids in enumerate(az_list['AvailabilityZones']):
    #     print(az_list['AvailabilityZones'][i]['ZoneName'])
    #     list1.append(az_list['AvailabilityZones'][i]['ZoneName'])
    subnet_list=datacentersdk.list_Subnets(ec2,vpc_id)
    sg_list=datacentersdk.list_securitygroup(ec2,vpc_id)
    keypair_list=datacentersdk.list_keypairs(ec2,vpc_id)
    
    svc_resp = {
        'region_name': region_name,
        'vpc_id': vpc_id,
        'azs': az_ids,
        'subnets': subnet_list,
        'securitygroup': sg_list,
        'keypair': keypair_list,        
        'create_date': create_date
    }

    response = Result(detail=svc_resp, status_code=3001)

    return response.make_resp()


