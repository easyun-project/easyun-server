# -*- coding: utf-8 -*-
"""
  @file:    datacenter_param.py
  @desc:    DataCenter Default Value Module
  @LastEditors:  Aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, REGION, FLAG, TagEasyun
from flask import jsonify
from  .datacenter_sdk import datacentersdk
from .schemas import DataCenterListOut

# define default parameters
default_name = 'Easyun'
# tag:Name prefix for all resource, eg. easyun-xxx
prefix = default_name.lower()+'-'
default_cidr = "10.10.0.0/16"

@bp.get('/default')
@auth_required(auth_token)
#@output(DataCenterListOut, description='Get DataCenter Info')
def get_datacentercfg():
    '''获取创建云数据中心默认参数'''

    # get account info from database
    curr_account:Account = Account.query.first()
    # set deploy_region as default region
    default_region = curr_account.get_region()

    # get az list
    client_ec2 = boto3.client('ec2', region_name=default_region)
    azs = client_ec2.describe_availability_zones()
    azList = [az['ZoneName'] for az in azs['AvailabilityZones']] 

    # define default igw
    default_igw = {
        # 这里为igw的 tag:Name，创建首个igw的时候默认该名称
        "tagName" : prefix+"igw"
    }

    # define default natgw
    default_natgw = {
        # 这里为natgw的 tag:Name ，创建首个natgw的时候默认该名称
        "tagName" : prefix+"natgw"
    }

    gwList = [default_igw["tagName"], default_natgw["tagName"]]

     # define default igw route table
    default_irtb = {
        # 这里为igw routetable 的 tag:Name, 创建首个igw routetable 的时候默认该名称
        "tagName" : prefix+"rtb-igw"
    }

    # define default natgw route table
    default_nrtb = {
        # 这里为nat routetable 的 tag:Name ，创建首个nat routetable 的时候默认该名称
        "tagName" : prefix+"rtb-natgw"
    }

    rtbList = [default_irtb["tagName"], default_nrtb["tagName"]]

    dcParameters = {
        # for DropDownList
        "azList": azList,
        "gwList" : gwList,
        "rtbList" : rtbList,
        # default selected parameters      
        "dcName" : default_name,
        "dcRegion" : default_region,
        "vpcCidr" : default_cidr,
        "pubSubnet1": {
            "tagName" : "Public subnet 1",
            "cidr" : "10.10.1.0/24",
            "az": azList[0],            
            "gateway": default_igw["tagName"],            
            "routeTable": default_irtb["tagName"] 
        },
        "pubSubnet2": {
            "tagName" : "Public subnet 2",
            "cidr" : "10.10.2.0/24",
            "az": azList[1],                
            "gateway": default_igw["tagName"],   
            "routeTable": default_irtb["tagName"]
        },
        "priSubnet1": {
            "tagName" : "Private subnet 1",
            "cidr" : "10.10.21.0/24",
            "az": azList[0],            
            "gateway": default_natgw["tagName"],             
            "routeTable": default_nrtb["tagName"]
        },
        "priSubnet2": {
            "tagName" : "Private subnet 2",
            "cidr" : "10.10.22.0/24",
            "az": azList[1],
            "gateway": default_natgw["tagName"],
            "routeTable": default_nrtb["tagName"]
        },
        "securityGroup0": {
            "tagName" : prefix+"sg-default",
            #该标记对应是否增加 In-bound: Ping 的安全组规则
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        },
        "securityGroup1": {
            "tagName" : prefix+"sg-webapp",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        },
        "securityGroup2": {
            "tagName" : prefix+"sg-database",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        },
        # keypair 在创建页面上没有体现，但会作为参数传回给add_datacenter的api
        "keypair" : "key_easyun_user"
    }

    response = Result(
        detail=dcParameters, 
        status_code=200
        )
    return response.make_resp()

