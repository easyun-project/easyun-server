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


@bp.get('/staticip')
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