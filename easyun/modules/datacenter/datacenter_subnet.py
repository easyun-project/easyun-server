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
from . import bp, DryRun
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from .schemas import DataCenterEIPIn,DataCenterListsIn,DataCenterListIn,DcParmIn,DataCenterSubnetIn,DataCenterSubnetInsert


@bp.get('/subnet')
#@auth_required(auth_token)
@input(DataCenterSubnetIn, location='query')
# # @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_subnet(param):
    '''获取数据中心 subnet 列表'''
    # only for globa regions
    # dc_name=request.args.get("dc_name")
    # type=request.args.get("subnet")

    dcName=param.get('dcName')
    subnetID=param.get('subnetID')
    
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    if thisDC == None:
        response = Result(detail ={'Result' : 'Errors'}, message='No Datacenter available, kindly create it first!', status_code=3001,http_status_code=400)
        response.err_resp()   

    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    subnetList = []    

    if subnetID == 'ALL' or subnetID is None :
        subnets = client_ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Flag', 'Values': [dcName]
                },             
            ],
            SubnetIds=[ 
                subnetID
            ]
        )
    else:
        subnets = client_ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Flag', 'Values': [dcName]
                },             
            ]
        )

    for subnet in subnets['Subnets']:
        subnet_id =  subnet['SubnetId']
        subnet_cidr =  subnet['CidrBlock']
        subnet_ipcount = subnet['AvailableIpAddressCount']
        subnet_record = {'SubnetId': subnet_id,
                'CidrBlock': subnet_cidr,
                'AvailableIpAddressCount': subnet_ipcount
        }
        subnetList.append(subnet_record)
    
    resp = Result(
        detail = subnetList,
        status_code=200
    )
    return resp.make_resp()

@bp.delete('/subnet')
# @auth_required(auth_token)
@input(DataCenterSubnetIn)
def delete_subnet(param):
    '''删除数据中心subnet mock'''
    dcName=param.get('dcName')
    subnetID=param.get('subnetID')

    dcTag = {"Key": "Flag", "Value": dcName}
  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    if (thisDC is None):
            response = Result(message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
            response.err_resp() 
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    try:
        response = client_ec2.delete_subnet(SubnetId=subnetID,DryRun=DryRun)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = Result(
                detail = [],
                status_code = 200 
            )
            return resp.make_resp()
        else:
            resp = Result(detail=[], status_code=2061)
            resp.err_resp()
    except Exception as ex:
        resp = Result(message='delete subnet failed due to invalid subnetID' ,status_code=2061,http_status_code=400)
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()

    resp = Result(
        detail = "subnet id got deleted!",
        status_code = 200 
    )
    return resp.make_resp()

@bp.post('/subnet')
#@auth_required(auth_token)
@input(DataCenterSubnetInsert)
# @output(DcResultOut, 201, description='add A new Datacenter')
def add_subnet(param):
    '''添加数据中心subnet mock'''
    dcName=param.get('dcName')
    subnetCIDR=param.get('subnetCDIR')

    dcTag = {"Key": "Flag", "Value": dcName}
  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    if (thisDC is None):
            response = Result(message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
            response.err_resp() 
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    nameTag = {"Key": "Name", "Value": "VPC-"+dcName}
       
    try:
        subnetID = client_ec2.create_subnet(
            CidrBlock=subnetCIDR, 
            VpcId=thisDC.vpc_id,
            TagSpecifications= [
                {
                    'ResourceType':'subnet', 
                    "Tags": [dcTag, nameTag]
                }
            ],
            DryRun=DryRun)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = Result(
                detail = [{'subnetID': subnetID['Subnet']['SubnetId']}],
                status_code = 200 
            )
            return resp.make_resp()
        else:
            resp = Result(detail=[], status_code=2061)
            resp.err_resp()
    except Exception as ex:
        resp = Result(message='create subnet failed due to invalid subnetID' ,status_code=2061,http_status_code=400)
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()

    resp = Result(
        detail = {"subnet id", 'subnet-123123'},
        status_code = 200 
    )
    return resp.make_resp()

