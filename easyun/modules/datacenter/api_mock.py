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
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from .schemas import DataCenterEIPIn,DataCenterListsIn,DataCenterListIn,DcParmIn,DataCenterSubnetIn
from . import bp,DryRun



@bp.get('/<service>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(ResourceListOut, description='Get DataCenter Resources')
def list_dc_service(service, parm):
    '''获取当前数据中心基础服务信息[Mock]'''
    # 数据中心基础服务区别于计算、存储、数据库等资源；
    # 数据中心基础服务包含： vpc、subnet、securitygroup、gateway、route、eip 等
    #
    # 先写在一个查询api里，建议拆分到每个服务模块里
    if service not in ['all','vpc','azone','subnet','secgroup','gateway','route','eip']:
        resp = Result(
            detail='Unknown input resource.',
            message='Validation error',
            status_code=2020,
            http_status_code=400
        )
        return resp.err_resp()

    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = parm['dc']).first()
        dcRegion = thisDC.get_region()
        # 设置 boto3 接口默认 region_name
        # boto3.setup_default_session(region_name = dcRegion )

        client_ec2 = boto3.client('ec2', region_name = dcRegion)
        resource_ec2 = boto3.resource('ec2', region_name = dcRegion)
        # vpcs = client_ec2.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': parm['dc']}])

        if service == 'vpc':
            '''获取数据中心 VPC 信息'''
            vpcId = thisDC.vpc_id            
            dcVPC = resource_ec2.Vpc(vpcId)
            vpcAttributes = {
                'tagName': [tag.get('Value') for tag in dcVPC.tags if tag.get('Key') == 'Name'][0],
                'vpcId':dcVPC.vpc_id,
                'cidrBlock':dcVPC.cidr_block,
                'vpcState':dcVPC.state,
                'vpcDefault':dcVPC.is_default
            }
            resp = Result(
                detail = vpcAttributes,
                status_code=200
            )

        if service == 'azone':
            '''获取数据中心 Availability Zone 信息'''
            # only for globa regions
            azs = client_ec2.describe_availability_zones()
            azList = [az['ZoneName'] for az in azs['AvailabilityZones']]            
            resp = Result(
                detail = azList,
                status_code=200
            )

        return resp.make_resp()
        
    except Exception as ex:
        resp = Result(
            detail=str(ex), 
            status_code=2030
        )
        return resp.err_resp()


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


# @bp.get('/staticip')
# #@auth_required(auth_token)
# @input(DataCenterListsIn, location='query')
# # @output(SubnetsOut, description='List DataCenter Subnets Resources')
# def list_datacenter(param):
#     '''获取数据中心 EIP 列表'''
#     # only for globa regions
#     # dc_name=request.args.get("vpc_idp")
#     dc_name=param['vpc_id']
#     type=param['type']
#     # type=request.args.get("eip")
    
#     if dc_name== 'ALL':
#         datacenters = Datacenter.query.all()


#     if (datacenters is None):
#         response = Result(detail ={'Result' : 'Errors'}, message='No Datacenter available, kindly create it first!', status_code=3001,http_status_code=400)
#         print(response.err_resp())
#         response.err_resp()   
    
#     for datacenter in datacenters:
#         vpc_id=datacenter.vpc_id
#         region_name=datacenter.region
#         create_date =datacenter.create_date
    
#     svc_resp = {
#         'region_name': region_name,
#         'vpc_id': vpc_id,
#         'azs': 'us-east-2',
#         # 'subnets': subnet_list,
#         # 'securitygroup': sg_list,
#         # 'keypair': keypair_list,        
#         'create_date': create_date
#     }

#     response = Result(detail=svc_resp, status_code=200)

#     return response.make_resp()
