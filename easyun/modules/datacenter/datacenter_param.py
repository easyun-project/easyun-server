# -*- coding: utf-8 -*-
"""
  @file:    datacenter_default.py
  @desc:    DataCenter Default Value Module
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, REGION, FLAG, TagEasyun
from flask import jsonify
from  .datacenter_sdk import datacentersdk
from .schemas import DataCenterListOut

DataCenterDft = {
    "region" : "us-east-1",
    "vpc_cidr" : "10.10.0.0/16",        
    "az_list": ["us-east-1a", "us-east-1b", "us-east-1c","us-east-1d","us-east-1e"], 
    "gw_list": ["easyun-igw", "easyun-nat"],
    "rt_list": ["easyun-route-igw","easyun-route-nat"],
    "pubSubnet1": {
        "name" : "Public subnet 1",
        "cidr" : "10.10.1.0/24",
        "az": "us-east-1a",
        "gateway":"easyun-igw",     
        # 这里为igw的 tag:Name ，创建首个igw的时候默认该名称
        "routeTable": "easyun-route-igw"    
        # 这里为igw routetable 的 tag:Name ，创建首个igw routetable 的时候默认该名称
    },
    "pubSubnet2": {
        "name" : "Public subnet 2",
        "cidr" : "10.10.2.0/24",
        "az": "us-east-1b",                        
        "gateway":"easyun-igw",   
        "routeTable": "easyun-route-igw"
    },
    "priSubnet1": {
        "name" : "Private subnet 1",
        "cidr" : "10.10.21.0/24",
        "az": "us-east-1a",
        "gateway": "easyun-nat",     
        # //这里为natgw的 tag:Name ，创建首个natgw的时候默认该名称
        "routeTable": "easyun-route-nat"  
        #//这里为nat routetable 的 tag:Name ，创建首个nat routetable 的时候默认该名称
    },
    "priSubnet2": {
        "name" : "Private subnet 2",
        "cidr" : "10.10.22.0/24",
        "az": "us-east-1b",
        "gateway": "easyun-nat",
        "routeTable": "easyun-route-nat"
    },
    "securityGroup1": {
        "name" : "easyun-sg-default",  
        #这里为 security group 的 tag:Name ，创建默认sg的时候默认该名称
        "enablePing": "true", 
        #该标记对应是否增加 In-bound: Ping 的安全组规则
        "enableSSH": "true",
        "eanbleRDP": "true"
    },
    "securityGroup2": {
        "name" : "easyun-sg-webapp",
        "enablePing": "true",
        "enableSSH": "true",
        "eanbleRDP": "true"
    },
    "securityGroup3": {
        "name" : "easyun-sg-database",
        "enablePing": "true",
        "enableSSH": "true",
        "eanbleRDP": "true"
    },
	# keypair 和 tags 在创建页面上没有体现，但会作为参数传回给add_datacenter的api
    "keypair" : "key_easyun_user",
    "tagsEasyun" : [
        {"Key": "Flag", "Value": "Easyun"}  
        #作为基础标签，后续创建每个资源的时候，在tagsEasyun列表基础上append 各资源的 Name 标签
    ]
},        

@bp.get('/default')
#@auth_required(auth_token)
#@output(DataCenterListOut, description='Get DataCenter Info')
def get_datacentercfg():
    '''获取创建云数据中心默认参数'''
    RESOURCE = boto3.resource('ec2', region_name=REGION)
    ec2 = boto3.client('ec2', region_name=REGION)
    
    # vpcs = ec2.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': [FLAG]}])
    response = Result(detail=DataCenterDft, status_code=200)
    return response.make_resp()

