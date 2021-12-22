# -*- coding: utf-8 -*-
"""
  @Description: DataCenter Management - action: start, restart, stop, delete; and get status
  @LastEditors: 
  @file:    datacenter_add.py
  @desc:    DataCenter Creation module
"""

from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from flask import current_app,jsonify
from datetime import date, datetime
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun import db, FLAG
import boto3
import os, time
import json
from . import bp, bp, DC_REGION, DC_NAME, VERBOSE,TagEasyun,DryRun
from  .datacenter_sdk import datacentersdk,app_log

# from . import vpc_act
from .schemas import DcParmIn, AddDatacenter, DataCenterResultOut

# from logging.handlers import RotatingFileHandler
import logging
from logging.handlers import RotatingFileHandler
from flask import current_app



# logger = logging.getLogger('test')

logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(threadName)s - %(thread)d - %(levelname)s - \n - %(message)s')
#formatter='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
file_handler = RotatingFileHandler('logs/easyun_api1.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# logger = logging.getLogger('test')
# logger.setLevel(logging.DEBUG)
# #logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(threadName)s - %(thread)d - %(levelname)s - \n - %(message)s')
file_handler1 = logging.FileHandler('logs/easyun_api3.log')
file_handler1.setLevel(logging.INFO)
file_handler1.setFormatter(formatter)

# define RotatingFileHandler，max 7 files with 100K per file

logger.addHandler(file_handler1)
logger.addHandler(file_handler)

a = datacentersdk()
# 云服务器参数定义
NewDataCenter = {
    'region': 'us-east-2',
    'vpc_cidr' : '10.10.0.0/16',
     "priSubnet1": {
        "az": "ap-northeast-1a",
        "cidr": "10.10.21.0/24",
        "gateway": "easyun-nat",
        "name": "Private subnet 1",
        "routeTable": "easyun-route-nat"
      },
      "priSubnet2": {
        "az": "ap-northeast-1b",
        "cidr": "10.10.22.0/24",
        "gateway": "easyun-nat",
        "name": "Private subnet 2",
        "routeTable": "easyun-route-nat"
      },
      "pubSubnet1": {
        "az": "ap-northeast-1a",
        "cidr": "10.10.1.0/24",
        "gateway": "easyun-igw",
        "name": "Public subnet 1",
        "routeTable": "easyun-route-igw"
      },
      "pubSubnet2": {
        "az": "ap-northeast-1b",
        "cidr": "10.10.2.0/24",
        "gateway": "easyun-igw",
        "name": "Public subnet 2",
        "routeTable": "easyun-route-igw"
      },
    'key' : "key_easyun_dev",
    "securityGroup1": {
        "eanbleRDP": "true",
        "enablePing": "true",
        "enableSSH": "true",
        "name": "easyun-sg-default"
      },
      "securityGroup2": {
        "eanbleRDP": "true",
        "enablePing": "true",
        "enableSSH": "true",
        "name": "easyun-sg-webapp"
      },
      "securityGroup3": {
        "eanbleRDP": "true",
        "enablePing": "true",
        "enableSSH": "true",
        "name": "easyun-sg-database"
      },
    'tag_spec' : [
        {
        "ResourceType":"instance",
        "Tags": [
                {"Key": "Flag", "Value": 'Easyun'},
                {"Key": "Name", "Value": 'test-from-api'}
            ]
        }
        ]
}



class DcResultOut(Schema):
    region_name = String()
    vpc_id = String()

@bp.post('/add_dc')
#@auth_required(auth_token)
@input(DcParmIn)
# @output(DcResultOut, 201, description='add A new Datacenter')
def add_datacenter(data):
    '''新增 Datacenter
    curl -X 'POST' \
  'http://127.0.0.1:6660/api/v1/datacenter/add_dc' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer cYOaaQ1Xj6Ejdap0tYcLLZrHWExs42Ll' \
  -H 'Content-Type: application/json' \
  -d ' {
       "keypair": "key_easyun_user",
      "priSubnet1": {
        "az": "ap-northeast-1a",
        "cidr": "10.10.21.0/24",
        "gateway": "easyun-nat",
        "name": "Private subnet 1",
        "routeTable": "easyun-route-nat"
      },
      "priSubnet2": {
        "az": "ap-northeast-1b",
        "cidr": "10.10.22.0/24",
        "gateway": "easyun-nat",
        "name": "Private subnet 2",
        "routeTable": "easyun-route-nat"
      },
      "pubSubnet1": {
        "az": "ap-northeast-1a",
        "cidr": "10.10.1.0/24",
        "gateway": "easyun-igw",
        "name": "Public subnet 1",
        "routeTable": "easyun-route-igw"
      },
      "pubSubnet2": {
        "az": "ap-northeast-1b",
        "cidr": "10.10.2.0/24",
        "gateway": "easyun-igw",
        "name": "Public subnet 2",
        "routeTable": "easyun-route-igw"
      },
      "region": "us-east-1",

      "securityGroup1": {
        "eanbleRDP": "true",
        "enablePing": "true",
        "enableSSH": "true",
        "name": "easyun-sg-default"
      },
      "securityGroup2": {
        "eanbleRDP": "true",
        "enablePing": "true",
        "enableSSH": "true",
        "name": "easyun-sg-webapp"
      },
      "securityGroup3": {
        "eanbleRDP": "true",
        "enablePing": "true",
        "enableSSH": "true",
        "name": "easyun-sg-database"
      },
      "tagsEasyun": [
        {
          "Key": "Flag",
          "Value": "Easyun"
        }
      ],
      "vpc_cidr": "10.10.0.0/16"
    }'
    '''
    # create easyun vpc
    # create 2 x pub-subnet
    # create 2 x pri-subnet
    # create 1 x easyun-igw (internet gateway)
    # create 1 x easyun-nat (nat gateway)
    # create 1 x easyun-route-igw
    # create 1 x easyun-route-nat
    # create 3 x easyun-sg-xxx
    # create 1 x key-easyun-user (默认keypair)
    # print(data)
    # logger.debug(data)
    region = data["region"]
    vpc_cidr = data["vpc_cidr"]
    public_subnet_1 = data["pubSubnet1"]
    public_subnet_2 = data["pubSubnet2"]
    private_subnet_1 = data["priSubnet1"]
    private_subnet_2 = data["priSubnet2"]
    keypair = data["keypair"]
    # sg_list= ['easyun-sg-default','easyun-sg-webapp','easyun-sg-database']

    sg_list=[]
    sg_list.append(data["securityGroup1"][0]["name"])
    sg_list.append(data["securityGroup2"][0]["name"])
    sg_list.append(data["securityGroup3"][0]["name"])

    # if data['sgs1_flag'] == 'True':
    #    sg_list.append('easyun-sg-default') 

    #a = datacentersdk()

    # print('haha'+str(sg_list))
    # logger.debug('haha'+str(sg_list))

    vpc_resource = boto3.resource('ec2', region_name=region)
    ec2 = boto3.client('ec2', region_name=region)
    # step 1: create VPC
    # TagEasyunVPC= [{'ResourceType':'vpc','Tags': TagEasyun}]

    svc_list_resp = []
    # query account id from DB (only one account for both phase 1 and 2) ????
    
    TagEasyunVPC= [ 
        {'ResourceType':'vpc', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": 'Easyun-vpc'}
            ]
        }
    ]
   
    try:
        vpc = vpc_resource.create_vpc(CidrBlock=vpc_cidr, TagSpecifications=TagEasyunVPC,DryRun=DryRun)
        print('VPC ID= '+ vpc.id )
        svc = {
        'region_name': DC_REGION,
        'vpc_id': vpc.id,
        }

        if datacentersdk.add_VPC_db(vpc.id,DC_REGION):
            logger.info('db operation is ok') 
        else:
            logger.info('db operation failed') 
            response = Result(message='DB Insert failed', status_code=2001,http_status_code=400)
            logger.info(response.err_resp())
            response.err_resp()   


        svc_list_resp.append(svc)
        logger.info('create_vpc1' + str(svc_list_resp))
        # response = Result(detail = svc, status_code=3001)
        # print(response.make_resp())
        # return response.make_resp()
    except Exception:
        response = Result(message='Datacenter VPC creation failed, maximum VPC reached', status_code=2001,http_status_code=400)
        logger.error('Datacenter VPC creation failed, maximum VPC reached')
        response.err_resp()   
        return


    # step 2: create Internet Gateway
    # Create and Attach the Internet Gateway
    # TagEasyunIG= [{'ResourceType':'internet-gateway','Tags': TagEasyun}]

    TagEasyunIG= [ 
        {'ResourceType':'internet-gateway', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": data["pubSubnet1"][0]['gateway']}
            ]
        }
    ]
    try:
        igw = ec2.create_internet_gateway(TagSpecifications=TagEasyunIG,DryRun=DryRun)
        logger.info(f'Internet gateway created with: {json.dumps(igw, indent=4)}')
        vpc.attach_internet_gateway(InternetGatewayId=igw['InternetGateway']['InternetGatewayId'],DryRun=DryRun)
        logger.info('Internet Gateway ID= '+ igw['InternetGateway']['InternetGatewayId'])
        
    except Exception:
        response = Result(message='Datacenter internet-gateway creation failed, maximum  reached', status_code=2001,http_status_code=400)
        logger.error('Datacenter internet-gateway creation failed, maximum  reached')
        response.err_resp()  
        return

    # Create a route table and a public route to Internet Gateway for public subnet
    # TagEasyunRouteTable= [{'ResourceType':'route-table','Tags': TagEasyun}]
    TagEasyunRouteTable= [ 
        {'ResourceType':'route-table', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": data["pubSubnet1"][0]['routeTable']}
            ]
        }
    ]
    try:
        igw_route_table = vpc.create_route_table(TagSpecifications=TagEasyunRouteTable,DryRun=DryRun)
        route = igw_route_table.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw['InternetGateway']['InternetGatewayId'],DryRun=DryRun
        )
        logger.info('Route Table ID= '+ igw_route_table.id)
    except Exception:
        response = Result(message='Datacenter igw_route_table creation failed, maximum  reached', status_code=2001,http_status_code=400)
        logger.error('Datacenter igw_route_table creation failed, maximum  reached')
        response.err_resp() 
        return

    # step 3: create 2 pub-subnet

    datacentersdk.add_subnet(ec2,vpc,igw_route_table,data["pubSubnet1"][0])
    datacentersdk.add_subnet(ec2,vpc,igw_route_table,data["pubSubnet2"][0])

# Create a route table and a public route to NAT Gateway for private subnet
    TagEasyunRouteTable= [ 
        {'ResourceType':'route-table', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": data["priSubnet1"][0]['routeTable']}
            ]
        }
    ]
    try:
        nat_route_table = vpc.create_route_table(TagSpecifications=TagEasyunRouteTable,DryRun=DryRun)
        route = nat_route_table.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw['InternetGateway']['InternetGatewayId'],DryRun=DryRun
        )
        logger.info('Route Table ID= '+ nat_route_table.id)
    except Exception:
        response = Result(message='Datacenter nat_route_table creation failed', status_code=2001,http_status_code=400)
        logger.error('Datacenter nat_route_table creation failed')
        response.err_resp() 
        return

    # create 2 private subnet
    natSubnetId=datacentersdk.add_subnet(ec2,vpc,nat_route_table,data["priSubnet1"][0])

    datacentersdk.add_subnet(ec2,vpc,nat_route_table,data["priSubnet2"][0])


    # Create public Subnet1
    # TagEasyunSubnet= [{'ResourceType':'subnet','Tags': TagEasyun}]
    
    # pub_subnet1 = ec2.create_subnet(CidrBlock=public_subnet_1, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
    # print('Public subnet1= '+ pub_subnet1['Subnet']['SubnetId'])

    # # associate the route table with the subnet
    # route_table.associate_with_subnet(SubnetId=pub_subnet1['Subnet']['SubnetId'])

    # step 2: create NAT Gateway and allocate EIP
    # allocate IPV4 address for NAT gateway

    TagEasyunEIP= [ 
        {'ResourceType':'elastic-ip', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": "Easyun-EIP"}
            ]
        }
    ]

    try:
        # Allocate EIP
        logger.info('Entering applying EIP')
        eip = ec2.allocate_address(Domain='vpc',DryRun=DryRun)
        logger.info(eip['PublicIp'])
    except Exception:
        response = Result(message='Datacenter allocate EIP failed', status_code=2001,http_status_code=400)
        logger.error('Datacenter allocate EIP failed')
        response.err_resp()   
        return

    TagEasyunNATGateway= [ 
        {'ResourceType':'natgateway', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": data["priSubnet1"][0]['gateway']}
            ]
        }
    ]
        # TagEasyunNATGateway= [{'ResourceType':'natgateway','Tags': TagEasyun}]
    
    try:    
        logger.info('Entering applying NAT Gateway and it will take about 1 min, Be patient!!!')

        response = ec2.create_nat_gateway(
            AllocationId=eip['AllocationId'],
            SubnetId=natSubnetId,
            TagSpecifications=TagEasyunNATGateway,
            ConnectivityType='public',
            DryRun=DryRun)

        nat_gateway_id = response['NatGateway']['NatGatewayId']
        logger.info(nat_gateway_id)
        
        # wait until the NAT gateway is available
        waiter = ec2.get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[nat_gateway_id])
    except Exception:
        response = Result(message='Datacenter NAT creation failed', status_code=2001,http_status_code=400)
        logger.error('Datacenter NAT creation failed')
        response.err_resp()   
        return

    # Step 5-1:  create security group easyun-sg-default
    # create security group allow SSH inbound rule through the VPC enable ssh/rdp/ping

    TagEasyunSecurityGroup= [{'ResourceType':'security-group','Tags': TagEasyun}]


    logger.info('Entering applying security group'+data["securityGroup1"][0]['name'])
    secure_groupid=datacentersdk.add_VPC_security_group(ec2,vpc,data["securityGroup1"][0])
    logger.info('secure_group1= '+secure_groupid)

    secure_groupid=datacentersdk.add_VPC_security_group(ec2,vpc,data["securityGroup2"][0])
    logger.info('secure_group1= '+secure_groupid)

    secure_groupid=datacentersdk.add_VPC_security_group(ec2,vpc,data["securityGroup3"][0])
    logger.info('secure_group1= '+secure_groupid)

    # secure_group1 = ec2.create_security_group(GroupName=sg, Description=sg_dict[sg], VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
    # ec2.authorize_security_group_ingress(
    #     GroupId=secure_group1['GroupId'],
    #     IpPermissions=IpPermissions1)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=3389, ToPort=3389)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='icmp', FromPort=-1, ToPort=-1)
    

    # create key pairs
    # TagEasyunKeyPair= [{'ResourceType':'key-pair','Tags': TagEasyun}]

    TagEasyunKeyPair= [ 
        {'ResourceType':'key-pair', 
            "Tags": [
            {"Key": "Flag", "Value": "Easyun"},
            {"Key": "Name", "Value": data['keypair']}
            ]
        }
    ]
    
    logger.info('Entering applying key pairs')

    try:
        new_keypair = vpc_resource.create_key_pair(KeyName=keypair,TagSpecifications=TagEasyunKeyPair,DryRun=DryRun)
        # keypair = 'key-easyun-user'
        if not os.path.exists('keys'):
            os.mkdir('keys')
        keypairfilename=keypair+'.pem'
        # with open('./keys/'+keypairfilename, 'w') as file:
        with open(os.path.join('./keys/',keypairfilename)) as file:
            file.write(new_keypair.key_material)
    except Exception:
        response = Result( message='Create key pairs failed due to already existed', status_code=2001,http_status_code=400)
        logger.info(response)
        

    # a.add_VPC_db(vpc,REGION)
    logger.info('create_vpc completion' + str(svc_list_resp))
    logger.info('create_vpc completion' + str(svc))
    # svc = {
    #     'region_name': REGION,
    #     'vpc_id': 'easyrun'
    # }
    response = Result(detail = svc, status_code=200)
    return response.make_resp()

