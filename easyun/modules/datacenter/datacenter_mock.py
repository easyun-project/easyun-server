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
from . import bp,DryRun
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from .schemas import DataCenterEIPIn,DataCenterListsIn,DataCenterListIn,DcParmIn,DataCenterSubnetIn

# @bp.get('/eip')
# #@auth_required(auth_token)
# @input(DataCenterEIPIn, location='query')
# # @output(SubnetsOut, description='List DataCenter Subnets Resources')
# def list_eip(param):
#     '''获取数据中心 EIP 列表'''
#     # only for globa regions
#     # dc_name=request.args.get("vpc_idp")
#     dcName=param.get('dcName')
#     eip_id=param.get('eip_id')
#     dcTag = {"Key": "Flag", "Value": dcName}

  
#     thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

#     if (thisDC is None):
#             response = Result(detail ={'Result' : 'Errors'}, message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
#             response.err_resp() 
  
#     client_ec2 = boto3.client('ec2', region_name= thisDC.region)

#     if type == 'ALL':
#         eips = client_ec2.describe_addresses(
#             Filters=[
#                 {
#                     'Name': 'tag:Flag', 'Values': [dcName]
#                 },             
#             ]
#         )
#     else:
#         eips = client_ec2.describe_addresses(
#             Filters=[
#                 {
#                     'Name': 'tag:Flag', 'Values': [dcName]
#                 },             
#             ]
#         )

#     eipList = []    

#     for eip in eips['Addresses']:
#         PublicIp =  eip['PublicIp']
#         AllocationId =  eip['AllocationId']
#         subnet_record = {'PublicIp': PublicIp,
#                 'AllocationId': AllocationId
#         }
#         eipList.append(subnet_record)

#     resp = Result(
#         detail = eipList,
#         status_code=200
#     )
#     return resp.make_resp()

# @bp.delete('/eip')
# # @auth_required(auth_token)
# @input(DataCenterEIPIn)
# def delete_eip(param):
#     dcName=param.get('dcName')
#     eipId=param.get('eip_id')
#     dcTag = {"Key": "Flag", "Value": dcName}
  
#     thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

#     if (thisDC is None):
#             response = Result(detail ={'Result' : 'Errors'}, message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
#             response.err_resp() 
  
#     client_ec2 = boto3.client('ec2', region_name= thisDC.region)

#     try:
#         response = client_ec2.release_address(AllocationId=eipId,DryRun=DryRun)

#         if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#             resp = Result(
#                 # detail = [{'AllocationId': eipId}],
#                 detail = [],
#                 status_code = 200 
#             )
#             return resp.make_resp()
#         else:
#             resp = Result(detail=[], status_code=2061)
#             resp.err_resp()
#     except Exception as ex:
#         resp = Result(message='release_address failed due to wrong AllocationId' , status_code=2061,http_status_code=400)
#         resp.err_resp()


# @bp.post('/eip')
# #@auth_required(auth_token)
# @input(DataCenterEIPIn)
# # @output(DcResultOut, 201, description='add A new Datacenter')
# def add_eip(param):
#     dcName=param.get('dcName')
#     type=param.get('eip_id')
#     dcTag = {"Key": "Flag", "Value": dcName}

  
#     thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

#     if (thisDC is None):
#             response = Result(detail ={'Result' : 'Errors'}, message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
#             response.err_resp() 
  
#     client_ec2 = boto3.client('ec2', region_name= thisDC.region)


#     try:
#         nameTag = {"Key": "Name", "Value": dcName.lower()+"-extra-eip"}
#         eip = client_ec2.allocate_address(
#             DryRun=DryRun,
#             Domain='vpc',
#             TagSpecifications = [
#                 {
#                     'ResourceType':'elastic-ip', 
#                     "Tags": [dcTag, nameTag]
#                 }
#             ]
#         )
        
#         eipList = [
#             {
#                 'PublicIp' : eip['PublicIp'],
#                 'AllocationId' : eip['AllocationId']
#             } ]
    
#     except Exception as ex:
#         resp = Result(detail=ex , status_code=2061)
#         resp.err_resp()

#     resp = Result(
#         detail = eipList,
#         status_code = 200 
#     )
#     return resp.make_resp()

@bp.get('/datacenter')
#@auth_required(auth_token)
@input(DataCenterListsIn, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_datacenter(param):
    '''获取数据中心 EIP 列表'''
    # only for globa regions
    # dc_name=request.args.get("vpc_idp")
    dc_name=param['vpc_id']
    type=param['type']
    # type=request.args.get("eip")
    
    if dc_name== 'ALL':
        datacenters = Datacenter.query.all()


    if (datacenters is None):
        response = Result(detail ={'Result' : 'Errors'}, message='No Datacenter available, kindly create it first!', status_code=3001,http_status_code=400)
        print(response.err_resp())
        response.err_resp()   
    
    for datacenter in datacenters:
        vpc_id=datacenter.vpc_id
        region_name=datacenter.region
        create_date =datacenter.create_date
    
    svc_resp = {
        'region_name': region_name,
        'vpc_id': vpc_id,
        'azs': 'us-east-2',
        # 'subnets': subnet_list,
        # 'securitygroup': sg_list,
        # 'keypair': keypair_list,        
        'create_date': create_date
    }

    response = Result(detail=svc_resp, status_code=200)

    return response.make_resp()


@bp.get('/azone/<dc_name>')
# @auth_required(auth_token)
# @input(DataCenterListsIn, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_azones(dc_name):
    '''获取数据中心 Availability Zone 列表'''
    # only for globa regions
    thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)
    azs = client_ec2.describe_availability_zones()
    azList = [az['ZoneName'] for az in azs['AvailabilityZones']] 

    resp = Result(
        detail = azList,
        status_code=200
    )
    return resp.make_resp()


@bp.get('/subnet/<dc_name>')
@auth_required(auth_token)
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_subnets(dc_name):
    '''获取数据中心现有资源: Subnet [mock]'''
    pubSubnet1 = {
        "tagName": "Public subnet 1",
        'subnetId':'subnet-06bfe659f6ecc2eed',
        'subnetType': 'public',
        "cidr": "10.10.1.0/24",
        "az": "us-east-1a",
        'freeIps': 249
    }
    pubSubnet2 = {
        "tagName": "Public subnet 2",
        'subnetId':'subnet-02a09fd044f6d8e8d',
        'subnetType': 'public',
        "cidr": "10.10.2.0/24",
        "az": "us-east-1b",
        'freeIps': 247
    }
    priSubnet1 = {
        "tagName": "Private subnet 1",
        'subnetId':'subnet-03c3de7f09dfe36d7',
        'subnetType': 'private',
        "cidr": "10.10.21.0/24",
        "az": "us-east-1a",
        'freeIps': 251
    }
    priSubnet2 = {
        "tagName": "Private subnet 2",
        'subnetId':'subnet-0c903785974d075f0',
        'subnetType': 'private',
        "cidr": "10.10.22.0/24",
        "az": "us-east-1b",
        'freeIps': 244
    }


    resp = Result(
        detail = [pubSubnet1,pubSubnet2,priSubnet1,priSubnet2],
        status_code=200
    )
    return resp.make_resp()


@bp.get('/secgroup')
#@auth_required(auth_token)
@input(DataCenterListIn, location='query')
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def list_secgroups(param):
    dc_name=param['vpc_id']
    type=param['seurityid']
    '''获取数据中心现有资源: SecurityGroup [mock]'''
    sgList = [
        {
            "tagName": "easyun-sg-default",
            'sgId': 'sg-0a818f9a74c0657ad',
            'sgDes': 'default VPC security group'
        },
        {
            "tagName": "easyun-sg-webapp",
            'sgId': 'sg-02f0f5390e1cba746',
            'sgDes': 'allow web application access'
        },
        {
            "tagName": "easyun-sg-database",
            'sgId': 'sg-05df5c8e8396d06e9',
            'sgDes': 'allow database access'
        }
    ]

    resp = Result(
        detail = sgList,
        status_code=200
    )
    return resp.make_resp()


@bp.delete('/securitygroup')
@auth_required(auth_token)
@input(DcParmIn)
def delete_securitygroup(param):
        
    TagEasyunSecurityGroup= [ 
        {'ResourceType':'security-group', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": 'securitygroup[name]'}
            ]
        }
    ]
        
    IpPermissions = () 
    IpPermissions.append({
            'IpProtocol': 'tcp',
            'FromPort': 3389,
            'ToPort': 3389,
            'IpRanges': [{
                'CidrIp': '0.0.0.0/0'
            }]
        })

    IpPermissions.append({
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{
                'CidrIp': '0.0.0.0/0'
            }]
        })
        
    resp = Result(
        detail = "securitygroup id=",
        status_code = 200 
    )

