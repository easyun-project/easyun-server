# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Get Module
  @desc:    数据中心相关信息GET API
  @auth:      
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.utils import len_iter, query_dc_region
from datetime import date, datetime
from . import bp, DC_NAME, DC_REGION, TagEasyun
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


@bp.get('')
@auth_required(auth_token)
# @output(DataCenterListOut, description='Get DataCenter List')
def list_datacenter_detail():
    '''获取Easyun管理的所有数据中心信息'''
    try:
        thisAccount:Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id = thisAccount.account_id)
        dcList = []
        for dc in dcs:
            resource_ec2 = boto3.resource('ec2', region_name= dc.region)
            vpc = resource_ec2.Vpc(dc.vpc_id)
            dcItem = {
                'dcName' : dc.name,
                'dcRegion' : dc.region,
                'vpcID' : dc.vpc_id,
                'vpcCidr' : vpc.cidr_block,
                'dcUser' : dc.create_user,
                'createDate' : dc.create_date.isoformat(),
                'createUser' : dc.create_user,
                'dcAccount' : dc.account_id,                
            }
            dcList.append(dcItem)
        
        resp = Result(
            detail = dcList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message="get datacebter list failed", 
            status_code=2001,
            http_status_code=400)
        response.err_resp()


@bp.get('/<dc_name>')
@auth_required(auth_token)
# @app_log('')
# @output(DCInfoOut, description='Get Datacenter Metadata')
def get_datacenter_detail(dc_name):
    '''获取指定的数据中心信息'''
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
        dcRegion = thisDC.get_region()

        resource_ec2 = boto3.resource('ec2', region_name= dcRegion)
        dcVPC = resource_ec2.Vpc(thisDC.vpc_id)
        dcItem = {
            'dcName' : thisDC.name,
            'dcRegion' : thisDC.region,
            'vpcID' : thisDC.vpc_id,
            'vpcCidr' : dcVPC.cidr_block,
            'createDate' : thisDC.create_date.isoformat(),
            'createUser' : thisDC.create_user,
            'dcAccount' : thisDC.account_id,
        }
        
        resp = Result(
            detail = dcItem,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=2012,http_status_code=400
        )
        response.err_resp()


@bp.get('/list')
@auth_required(auth_token)
# @output(DataCenterListOut, description='Get DataCenter List')
def list_datacenter_brief():
    '''获取Easyun管理的数据中心列表[仅基础字段]'''
    try:
        thisAccount:Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id = thisAccount.account_id)
        dcList = []
        for dc in dcs:
            dcItem = {
                'dcName' : dc.name,
                'dcRegion' : dc.region,
                'vpcID' : dc.vpc_id
            }
            dcList.append(dcItem)
        
        resp = Result(
            detail = dcList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, 
            status_code=2001,
            http_status_code=400)
        response.err_resp()


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




        # datacenters:Datacenter  = Datacenter.query.filter_by(id=1).first()
        # datacenters:Datacenter  = Datacenter.query.get(1)

        # datacenters = Datacenter.query.first()
        # if len(datacenters) == 0:
        # if (datacenters is None):
        #     response = Result(detail ={'Result' : 'Errors'}, message='No Datacenter available, kindly create it first!', status_code=3001,http_status_code=400)
        #     print(response.err_resp())
        #     response.err_resp()   
        # else:
        #     vpc_id=datacenters.vpc_id
        #     region_name=datacenters.region
        #     create_date =datacenters.create_date
        
        #     current_app.logger.debug("AAAA"+vpc_id)
        #     current_app.logger.info("AAAA"+str(region_name))

        # regions = ec2.describe_regions(Filters=[{'Name': 'region-name','Values': [REGION]}])

        # az_list = client_ec2.describe_availability_zones(Filters=[{'Name': 'group-name','Values': [DC_REGION]}])

        # az_ids = [ az['ZoneName'] for az in az_list['AvailabilityZones'] ]

    #    list1=[]
        # for i in range(len(az_list['AvailabilityZones'])):
        # for i, azids in enumerate(az_list['AvailabilityZones']):
        #     print(az_list['AvailabilityZones'][i]['ZoneName'])
        #     list1.append(az_list['AvailabilityZones'][i]['ZoneName'])

        
        # subnet_list=datacentersdk.list_Subnets(client_ec2,vpc_id)
        # sg_list=datacentersdk.list_securitygroup(client_ec2,vpc_id)
        # keypair_list=datacentersdk.list_keypairs(client_ec2,vpc_id)
        
        # svc_resp = {
        #     'region_name': region_name,
        #     'vpc_id': vpc_id,
        #     'azs': az_ids,
        #     'subnets': subnet_list,
        #     'securitygroup': sg_list,
        #     'keypair': keypair_list,        
        #     'create_date': create_date
        # }

        # response = Result(detail=svc_resp, status_code=200)

        # return response.make_resp()
