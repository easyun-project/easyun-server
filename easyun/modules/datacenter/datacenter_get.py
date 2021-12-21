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
from easyun.common.models import Account,Datacenter
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, DC_NAME, DC_REGION, TagEasyun
from flask import jsonify,send_file, send_from_directory,make_response
import os
from  .datacenter_sdk import datacentersdk,app_log

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
from .schemas import DataCenter2ListOut

NewDataCenter = {
    'region': 'us-east-1',
    'vpc_cidr' : '10.10.0.0/16',
    'avaibility_zone' : 'us-east-1a',
    'pub_subnet1' : '10.10.1.0/24',
    'pub_subnet2' : '10.10.2.0/24',
    'pri_subnet1' : '10.10.3.0/24',
    'pri_subnet2' : '10.10.4.0/24',
    'key' : "key_easyun_dev",
    'secure_group1' : 'easyun-sg-default',
    'secure_group2' : 'easyun-sg-webapp',
    'secure_group3' : 'easyun-sg-database',
    'tag_spec' : [
        {
        "ResourceType":"vpc",
        "Tags": [
                {"Key": "Flag", "Value": FLAG},
                {"Key": "Name", "Value": DC_NAME}
            ]
        }
        ]
}

    
@app_log('download keypair')
@bp.get('/downloadkeypair/<keyname>')
# @auth_required(auth_token)
def download_keypair(keyname):
   '''获取Easyun环境下keypair'''
   path = os.path.join(os.getcwd(),'keys')  # 假设在当前目录
   
# keypair_name = 'key-easyun-user'

   keypairfilename=keyname+'.pem'

   if os.path.exists(os.path.join(path,keypairfilename)):
   
     with open(os.path.join('./keys/',keypairfilename)) as file:
            response = make_response(send_from_directory(path, keypairfilename, as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(keypairfilename.encode().decode('latin-1'))
            return response
   else:
       response = Result( message='Keypair file doesn\'t exist', status_code=2001,http_status_code=400)
       current_app.logger.info(response)
       response.err_resp()  


@bp.get('/all')
#@auth_required(auth_token)
@output(DataCenter2ListOut, description='Get DataCenter Region Info')
def get_datacenter_all():
    '''获取Easyun环境下云数据中心信息'''
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

    # print(vpc_id)
    # print(datacenters.id)


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


@bp.get('/testget')
#@auth_required(auth_token)
def testget():
    '''数据中心测试专用'''
    directory = os.getcwd()  # 假设在当前目录
    ec2 = boto3.client('ec2', region_name=DC_REGION)
    vpc_resource = boto3.resource('ec2', region_name=DC_REGION)
    TagEasyunKeyPair= [{'ResourceType':'key-pair','Tags': TagEasyun}]
    keypair_filename="key_easyun_user"
    try:
        # if not os.path.exists('keys'):
        #     os.mkdir('keys')
        new_keypair = vpc_resource.create_key_pair(KeyName=keypair_filename,TagSpecifications=TagEasyunKeyPair)
        # keypair_name = 'key-easyun-user'
        with open('./'+keypair_filename, 'w') as file:
            file.write(new_keypair.key_material)
            print(new_keypair)
    except Exception:
            response = Result(detail ={'Result' : 'Errors'}, message='Create key pairs failed due to already existed', status_code=3001,http_status_code=400)
            print(response)
            current_app.logger.debug(response)
    #    return send_from_directory(directory, filename, as_attachment=True)
    response = make_response(send_from_directory(directory, keypair_filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(keypair_filename.encode().decode('latin-1'))
    return response