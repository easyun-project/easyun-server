# -*- coding: utf-8 -*-
"""
  @file:    datacenter_get.py
  @desc:    DataCenter Get module
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, DC_NAME, DC_REGION, TagEasyun
from flask import jsonify,send_file, send_from_directory,make_response
import os
from .datacenter_sdk import datacentersdk,app_log
from .schemas import ResourceListOut, DataCenterListOut, DCInfoOut, VpcListOut,DataCenterListIn

# from logging.handlers import RotatingFileHandler
# import logging
# from logging.handlers import RotatingFileHandler
from flask import current_app



# # logger = logging.getLogger('test')

# logger = logging.getLogger()
# formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(threadName)s - %(thread)d - %(levelname)s - \n - %(message)s')
# #formatter='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
# file_handler = RotatingFileHandler('logs/easyun_api1.log', maxBytes=10240, backupCount=10)
# file_handler.setFormatter(formatter)
# file_handler.setLevel(logging.DEBUG)

# # logger = logging.getLogger('test')
# # logger.setLevel(logging.DEBUG)
# # #logger.setLevel(logging.DEBUG)
# # formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(threadName)s - %(thread)d - %(levelname)s - \n - %(message)s')
# file_handler1 = logging.FileHandler('logs/easyun_api3.log')
# file_handler1.setLevel(logging.INFO)
# file_handler1.setFormatter(formatter)

# # define RotatingFileHandler，max 7 files with 100K per file

# logger.addHandler(file_handler1)
# logger.addHandler(file_handler)

@bp.get('/quota')
#@auth_required(auth_token)
@input(DataCenterListIn, location='query')
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def list_dcquota(param):
    '''获取数据中心资源配额 [mock]'''
    dcName=param.get('dcName')
    
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    if (thisDC is None):
            response = Result(message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
            response.err_resp() 
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    resource_ec2 = boto3.resource('ec2', region_name= thisDC.region)
    vpc = resource_ec2.Vpc(thisDC.vpc_id)
    noVPCUsed = len(list(resource_ec2.vpcs.all()))
    noSecurityGroupUsed = len(list(resource_ec2.security_groups.all()))
    noSubnetsUsed = len(list(resource_ec2.subnets.all()))
    noEIPUsed = len(list(resource_ec2.vpc_addresses.all()))
    noIGUsed = len(list(resource_ec2.internet_gateways.all()))
    noNetworkInterfaceUsed = len(list(resource_ec2.network_interfaces.all()))


    vpcUsageLimit = []
    limitVPC = {
            'vpc limit' : 5,
            'EIP limit' : 5,
            'NAT limit' : 5,
            'Internet Gateway Limit': 10,
            'Network Interface Limit': 10,
            'Security Group Limit' : 5,
            'Subnet Limit': 200
            }

    usageVPC = {
            'vpc number used' : noVPCUsed,
            'EIP used' : noEIPUsed,
            'NAT used' : 5,
            'Internet Gateway used': noIGUsed,
            'Network Interface used': noNetworkInterfaceUsed,
            'Security Group used' : noSecurityGroupUsed,
            'Subnet Used': noSubnetsUsed
            }
    vpcUsageLimit.append(limitVPC)
    vpcUsageLimit.append(usageVPC)

        
    resp = Result(
        detail = vpcUsageLimit,
        status_code=200
    )
    return resp.make_resp()

    # dcUsageList = [
    #     {
    #         "vpcname": "vip1",
    #         'vpcId': 'vpc-0a818f9a74c0657ad',
    #         'EIP usage': '3/5 is being used',
    #         'Subnet usage': '3/5 is being used'
    #     },
    #     {
    #         "vpcname": "vip2",
    #         'vpcId': 'vpc-0a818f9a74c0657ad',
    #         'EIP usage': '3/5 is being used',
    #         'Subnet usage': '3/5 is being used'
    #     }
    # ]

    # resp = Result(
    #     detail = dcUsageList,
    #     status_code=200
    # )
    # return resp.make_resp()

   
# @app_log('download keypair')
# @bp.get('/downloadkeypair/<keyname>')
# # @auth_required(auth_token)
# def download_keypair(keyname):
#    '''获取Easyun环境下keypair'''
#    path = os.path.join(os.getcwd(),'keys')  # 假设在当前目录
   
# # keypair_name = 'key-easyun-user'

#    keypairfilename=keyname+'.pem'

#    if os.path.exists(os.path.join(path,keypairfilename)):
   
#      with open(os.path.join('./keys/',keypairfilename)) as file:
#             response = make_response(send_from_directory(path, keypairfilename, as_attachment=True))
#             response.headers["Content-Disposition"] = "attachment; filename={}".format(keypairfilename.encode().decode('latin-1'))
#             return response
#    else:
#        response = Result( message='Keypair file doesn\'t exist', status_code=2001,http_status_code=400)
#        current_app.logger.info(response)
#        response.err_resp() 


@bp.get('/list')
# @auth_required(auth_token)
# @output(DataCenterListOut, description='Get DataCenter List')
def list_all_datacenter():
    '''获取Easyun管理的数据中心列表---已经废除，请使用/'''
    try:
        curr_account:Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id = curr_account.account_id)
        dcList = [] 
        for dc in dcs:
            resource_ec2 = boto3.resource('ec2', region_name= dc.region)
            vpc = resource_ec2.Vpc(dc.vpc_id)
            dcItem = {
                'dcName' : dc.name,
                'dcRegion' : dc.region,
                'vpcID' : dc.vpc_id,
                # 'vpcCidr' : vpc.cidr_block,
                'dcUser' : dc.create_user
            }
            dcList.append(dcItem)
        
        resp = Result(
            detail = dcList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(message="get datacebter list failed", status_code=2001,http_status_code=400)
        response.err_resp()


@bp.get('/')
# @auth_required(auth_token)
# @output(DataCenterListOut, description='Get DataCenter List')
def list_all_datacenters():
    '''获取Easyun管理的数据中心列表'''
    try:
        curr_account:Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id = curr_account.account_id)
        dcList = [] 
        for dc in dcs:
            resource_ec2 = boto3.resource('ec2', region_name= dc.region)
            vpc = resource_ec2.Vpc(dc.vpc_id)
            dcItem = {
                'dcName' : dc.name,
                'dcRegion' : dc.region,
                'vpcID' : dc.vpc_id,
                # 'vpcCidr' : vpc.cidr_block,
                'dcUser' : dc.create_user
            }
            dcList.append(dcItem)
        
        resp = Result(
            detail = dcList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(message="get datacebter list failed", status_code=2001,http_status_code=400)
        response.err_resp()



@bp.get('/<dc_name>')
@auth_required(auth_token)
# @app_log('')
@output(DCInfoOut, description='Get Datacenter Metadata')
def get_datacenter_info(dc_name):
    '''获取当前数据中心基础信息'''
    try:
        dc = Datacenter.query.filter_by(name = dc_name).first()
        resource_ec2 = boto3.resource('ec2', region_name= dc.region)
        vpc = resource_ec2.Vpc(dc.vpc_id)
        dcItem = {
            'dcName' : dc.name,
            'dcRegion' : dc.region,
            'vpcID' : dc.vpc_id,
            'vpcCidr' : vpc.cidr_block,
            'dcUser' : dc.create_user,
            'dcAccount' : dc.name
        }
        
        resp = Result(
            detail = dcItem,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=2002,http_status_code=400
        )
        response.err_resp()
    


@bp.get('/all/<dc_name>')
#@auth_required(auth_token)
@output(ResourceListOut, description='Get DataCenter Resources')
def get_resources(dc_name):
    '''获取当前数据中心全部资源信息'''
    # get vpc info
    # get subnet info
    # get securitygroup info
    # get keypair info

    RESOURCE = boto3.resource('ec2', region_name=DC_REGION)
    ec2 = boto3.client('ec2', region_name=DC_REGION)

    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': [DC_NAME]}])

    # vpcs = client1.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': [FLAG]}])

    datacenters:Datacenter  = Datacenter.query.filter_by(id=1).first()
    # datacenters:Datacenter  = Datacenter.query.get(1)

    # datacenters = Datacenter.query.first()
    # if len(datacenters) == 0:
    if (datacenters is None):
        response = Result(detail ={'Result' : 'Errors'}, message='No Datacenter available, kindly create it first!', status_code=3001,http_status_code=400)
        print(response.err_resp())
        response.err_resp()   
    else:
        vpc_id=datacenters.vpc_id
        region_name=datacenters.region
        create_date =datacenters.create_date
    
        current_app.logger.debug("AAAA"+vpc_id)
        current_app.logger.info("AAAA"+str(region_name))

    # regions = ec2.describe_regions(Filters=[{'Name': 'region-name','Values': [REGION]}])

    az_list = ec2.describe_availability_zones(Filters=[{'Name': 'group-name','Values': [DC_REGION]}])

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

    response = Result(detail=svc_resp, status_code=200)

    return response.make_resp()


