# -*- coding: utf-8 -*-
"""
  @author:  pengchang
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited. 
  @file:    datacenter_get.py
  @desc:    The DataCenter Get module
"""
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, REGION, FLAG
from flask import jsonify

NewDataCenter = {
    'region': 'us-east-2',
    'vpc_cidr' : '10.10.0.0/16',
    'avaibility_zone' : '10.10.0.0/16',
    'pub_subnet1' : '192.168.1.0/24',
    'pub_subnet2' : '192.168.2.0/24',
    'pri_subnet1' : '192.168.3.0/24',
    'pri_subnet2' : '192.168.4.0/24',
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
    az = String()
    

@bp.get('/datacenter/all')
@auth_required(auth_token)
@output(DataCenterListOut, description='Get DataCenter Region Info')
def get_datacenter_all():
    '''获取Easyun环境下云数据中心信息'''
    RESOURCE = boto3.resource('ec2', region_name=REGION)
    ec2 = boto3.client('ec2', region_name=REGION)

    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'tag:FLAG','Values': [FLAG]}])

    regions = ec2.describe_regions(Filters=[{'Name': 'region-name','Values': [REGION]}])

    azs = ec2.describe_availability_zones(Filters=[{'Name': 'group-name','Values': [REGION]}])

    list1=[]
    for i in range(len(azs['AvailabilityZones'])):
        print(azs['AvailabilityZones'][i]['ZoneName'])
        list1.append(azs['AvailabilityZones'][i]['ZoneName'])

    svc_resp = {
        'region': REGION,
        'vpc_id': 'easyrun',
        'azs': list1
    }

    response = Result(detail = svc_resp, status_code=3001)

    return response.make_resp()


@bp.get('/datacenter/AZ')
@auth_required(auth_token)
@output(DataCenterListOut, description='Get DataCenter AZ Info')
def get_datacenter_AZ():
    '''获取Easyun环境下云数据中心信息'''
    RESOURCE = boto3.resource('ec2', region_name=REGION)
    ec2 = boto3.client('ec2', region_name=REGION)

    try:
        azs = ec2.describe_availability_zones(Filters=[{'Name': 'group-name','Values': [REGION],}])
        
        list1=[]
        for i in range(len(azs['AvailabilityZones'])):
            print(azs['AvailabilityZones'][i]['ZoneName'])
            list1.append(azs['AvailabilityZones'][i]['ZoneName'])
        print('az1',str(list1))

        list_resp = []
        svc = {
            'region': REGION,
            'vpc_id': 'easyrun',
            'azs': list1
        }

        list_resp.append(svc)
        print('haha' + str(list_resp))

        response = Result(detail = list_resp, status_code=3001)

        print(response.make_resp())
        return response.make_resp()

    except Exception:
        response = Result(message='datacenter query failed', status_code=3001,http_status_code=400)
        response.err_resp()    
