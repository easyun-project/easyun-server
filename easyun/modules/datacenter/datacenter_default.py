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
from easyun.common.models import Account, Datacenter
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.schemas import DcNameQuery
from .schemas import DataCenterListOut
from . import bp, REGION, FLAG, TagEasyun


@bp.get('/default')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
#@output(DataCenterListOut, description='Get DataCenter Info')
def get_default_parms(parm):
    '''获取创建云数据中心默认参数'''
    inputName = parm['dc']
    try:
        # Check if the DC Name is available
        thisDC:Datacenter = Datacenter.query.filter_by(name = inputName).first()
        if (thisDC is not None):
            raise ValueError('DataCenter name already existed')

        # tag:Name prefix for all resource, eg. easyun-xxx
        prefix = inputName.lower()

        # get account info from database
        curr_account:Account = Account.query.first()
        # set deploy_region as default region
        defaultRegion = curr_account.get_region()

        # get az list
        client_ec2 = boto3.client('ec2', region_name=defaultRegion)
        azs = client_ec2.describe_availability_zones()
        azList = [az['ZoneName'] for az in azs['AvailabilityZones']] 

        # define default vpc parameters
        defaultVPC = {
            'cidrBlock' : '10.10.0.0/16',
            # 'vpcCidrv6' : '',
            # 'vpcTenancy' : 'Default',
        }

        # define default igw
        defaultIgw = {
            # 这里为igw的 tag:Name，创建首个igw的时候默认该名称
            "tagName" : '%s-%s' %(prefix, 'igw')
        }

        # define default natgw
        defaultNatgw = {
            # 这里为natgw的 tag:Name ，创建首个natgw的时候默认该名称
            "tagName" : '%s-%s' %(prefix, 'natgw')
        }

        gwList = [defaultIgw["tagName"], defaultNatgw["tagName"]]

        # define default igw route table
        defaultIrtb = {
            # 这里为igw routetable 的 tag:Name, 创建首个igw routetable 的时候默认该名称
            "tagName" : '%s-%s' %(prefix, 'rtb-igw')
        }

        # define default natgw route table
        defaultNrtb = {
            # 这里为nat routetable 的 tag:Name ，创建首个nat routetable 的时候默认该名称
            "tagName" : '%s-%s' %(prefix, 'rtb-natgw')
        }

        rtbList = [defaultIrtb["tagName"], defaultNrtb["tagName"]]

        dcParms = {    
            # default selected parameters      
            "dcName" : inputName,
            "dcRegion" : defaultRegion,
            'dcVPC' : defaultVPC,
            "pubSubnet1": {
                "tagName" : "Public subnet 1",
                "cidrBlock" : "10.10.1.0/24",
                "azName": azList[0],            
                "gwName": defaultIgw["tagName"],            
                "routeTable": defaultIrtb["tagName"] 
            },
            "pubSubnet2": {
                "tagName" : "Public subnet 2",
                "cidrBlock" : "10.10.2.0/24",
                "azName": azList[1],                
                "gwName": defaultIgw["tagName"],   
                "routeTable": defaultIrtb["tagName"]
            },
            "priSubnet1": {
                "tagName" : "Private subnet 1",
                "cidrBlock" : "10.10.21.0/24",
                "azName": azList[0],            
                "gwName": defaultNatgw["tagName"],             
                "routeTable": defaultNrtb["tagName"]
            },
            "priSubnet2": {
                "tagName" : "Private subnet 2",
                "cidrBlock" : "10.10.22.0/24",
                "azName": azList[1],
                "gwName": defaultNatgw["tagName"],
                "routeTable": defaultNrtb["tagName"]
            },
            "securityGroup0": {
                "tagName" : '%s-%s' %(prefix, 'sg-default'),
                #该标记对应是否增加 In-bound: Ping 的安全组规则
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False
            },
            "securityGroup1": {
                "tagName" : '%s-%s' %(prefix, 'sg-webapp'),
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False
            },
            "securityGroup2": {
                "tagName" : '%s-%s' %(prefix, 'sg-database'),
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False
            },

        }
        dropDown = {
            # for DropDownList
            "azList": azList,
            "gwList" : gwList,
            "rtbList" : rtbList,
        }    

        response = Result(
            detail={
                'dcParms':dcParms, 
                'dropDown':dropDown
            },
            status_code=200
            )
        return response.make_resp()

    except Exception as ex:
        resp = Result(
            message=str(ex), 
            status_code=2001,
            http_status_code=400)
        resp.err_resp()