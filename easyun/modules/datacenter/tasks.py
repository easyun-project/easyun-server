#!/usr/bin/env python
# encoding: utf-8
"""
  @author:  shui
  @file:    tasks.py
  @time:    2021/12/28 22:28
  @desc:
"""
import boto3
import os
import json
from . import DC_REGION, TagEasyun, DryRun
from .datacenter_sdk import datacentersdk
from easyun import celery


import logging
from logging.handlers import RotatingFileHandler
from flask import current_app

# logger = logging.getLogger('test')

logger = logging.getLogger()
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - %(threadName)s - %(thread)d - %(levelname)s - \n - %(message)s')
# formatter='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
file_handler = RotatingFileHandler('logs/easyun_api1.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

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


def format_res(msg, code, http_code=200):
    return {
        'msg': msg,
        'code': code,
        'http_code': http_code
    }
@celery.task()
def add_datacenter_task(data):
    """
    新增 Datacenter 异步任务
    按步骤进行，步骤失败直接返回
    :return {msg: code: http_code:默认200，不建议传值}
    """
    # create easyun vpc
    # create 2 x pub-subnet
    # create 2 x pri-subnet
    # create 1 x easyun-igw (internet gateway)
    # create 1 x easyun-nat (nat gateway)
    # create 1 x easyun-route-igw
    # create 1 x easyun-route-nat
    # create 3 x easyun-sg-xxx
    # create 1 x key-easyun-user (默认keypair)
    region = data["region"]
    vpc_cidr = data["vpc_cidr"]
    public_subnet_1 = data["pubSubnet1"]
    public_subnet_2 = data["pubSubnet2"]
    private_subnet_1 = data["priSubnet1"]
    private_subnet_2 = data["priSubnet2"]
    keypair = data["keypair"]


    vpc_resource = boto3.resource('ec2', region_name=region)
    ec2 = boto3.client('ec2', region_name=region)
    # step 1: create VPC
    # TagEasyunVPC= [{'ResourceType':'vpc','Tags': TagEasyun}]

    # query account id from DB (only one account for both phase 1 and 2) ????

    TagEasyunVPC = [
        {'ResourceType': 'vpc',
         "Tags": [
             {"Key": "Flag", "Value": "Easyun"},
             {"Key": "Name", "Value": 'Easyun-vpc'}
         ]
         }
    ]

    try:
        vpc = vpc_resource.create_vpc(CidrBlock=vpc_cidr, TagSpecifications=TagEasyunVPC, DryRun=DryRun)
        logger.info('VPC ID= ' + vpc.id)
        svc = {
            'region_name': DC_REGION,
            'vpc_id': vpc.id,
        }

        if datacentersdk.add_VPC_db(vpc.id, DC_REGION) == True:
            logger.info('db operation is ok')
        else:
            logger.info('db operation failed')
            return format_res(
                msg='DB Insert failed',
                code=2001
            )


        logger.info('create_vpc1' + str(svc))
        # response = Result(detail = svc, status_code=3001)
        # return response.make_resp()
    except Exception as e:
        # response = Result(message='Datacenter VPC creation failed, maximum VPC reached', status_code=2001,http_status_code=400)
        logger.error('Datacenter VPC creation failed, maximum VPC reached')
        return format_res(
            msg=e,
            code=2001
        )

        # step 2: create Internet Gateway
    # Create and Attach the Internet Gateway
    # TagEasyunIG= [{'ResourceType':'internet-gateway','Tags': TagEasyun}]

    TagEasyunIG = [
        {'ResourceType': 'internet-gateway',
         "Tags": [
             {"Key": "Flag", "Value": "Easyun"},
             {"Key": "Name", "Value": data["pubSubnet1"][0]['gateway']}
         ]
         }
    ]
    try:
        igw = ec2.create_internet_gateway(TagSpecifications=TagEasyunIG, DryRun=DryRun)
        logger.info(f'Internet gateway created with: {json.dumps(igw, indent=4)}')
        vpc.attach_internet_gateway(InternetGatewayId=igw['InternetGateway']['InternetGatewayId'], DryRun=DryRun)
        logger.info('Internet Gateway ID= ' + igw['InternetGateway']['InternetGatewayId'])

    except Exception:
        logger.error('Datacenter internet-gateway creation failed, maximum  reached')
        return format_res(
            msg='Datacenter internet-gateway creation failed, maximum  reached',
            code=2001
        )

    # Create a route table and a public route to Internet Gateway for public subnet
    # TagEasyunRouteTable= [{'ResourceType':'route-table','Tags': TagEasyun}]
    TagEasyunRouteTable = [
        {'ResourceType': 'route-table',
         "Tags": [
             {"Key": "Flag", "Value": "Easyun"},
             {"Key": "Name", "Value": data["pubSubnet1"][0]['routeTable']}
         ]
         }
    ]
    try:
        igw_route_table = vpc.create_route_table(TagSpecifications=TagEasyunRouteTable, DryRun=DryRun)
        route = igw_route_table.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw['InternetGateway']['InternetGatewayId'], DryRun=DryRun
        )
        logger.info('Route Table ID= ' + igw_route_table.id)
    except Exception:
        logger.error('Datacenter igw_route_table creation failed, maximum  reached')
        return format_res(
            msg='Datacenter igw_route_table creation failed, maximum  reached',
            code=2001
        )

    # step 3: create 2 pub-subnet

    datacentersdk.add_subnet(ec2, vpc, igw_route_table, data["pubSubnet1"])
    datacentersdk.add_subnet(ec2, vpc, igw_route_table, data["pubSubnet2"])

    # Create a route table and a public route to NAT Gateway for private subnet
    TagEasyunRouteTable = [
        {'ResourceType': 'route-table',
         "Tags": [
             {"Key": "Flag", "Value": "Easyun"},
             {"Key": "Name", "Value": data["priSubnet1"][0]['routeTable']}
         ]
         }
    ]
    try:
        nat_route_table = vpc.create_route_table(TagSpecifications=TagEasyunRouteTable, DryRun=DryRun)
        route = nat_route_table.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw['InternetGateway']['InternetGatewayId'], DryRun=DryRun
        )
        logger.info('Route Table ID= ' + nat_route_table.id)
    except Exception:
        logger.error('Datacenter nat_route_table creation failed')
        return format_res(
            msg='Datacenter nat_route_table creation failed',
            code=2001
        )

    # create 2 private subnet

    natSubnetId = datacentersdk.add_subnet(ec2, vpc, nat_route_table, data["priSubnet1"])

    datacentersdk.add_subnet(ec2, vpc, nat_route_table, data["priSubnet2"])

    # step 2: create NAT Gateway and allocate EIP
    # allocate IPV4 address for NAT gateway

    TagEasyunEIP = [
        {'ResourceType': 'elastic-ip',
         "Tags": [
             {"Key": "Flag", "Value": "Easyun"},
             {"Key": "Name", "Value": "Easyun-EIP"}
         ]
         }
    ]

    try:
        # Allocate EIP
        logger.info('Entering applying EIP')
        eip = ec2.allocate_address(Domain='vpc', DryRun=DryRun)
        logger.info(eip['PublicIp'])
    except Exception as e:
        logger.error(e)
        return format_res(
            msg='Datacenter allocate EIP failed',
            code=2001
        )

    TagEasyunNATGateway = [
        {'ResourceType': 'natgateway',
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
        logger.error('Datacenter NAT creation failed')
        return format_res(
            msg='Datacenter NAT creation failed',
            code=2001
        )

        # Step 5-1:  create security group easyun-sg-default
    # create security group allow SSH inbound rule through the VPC enable ssh/rdp/ping

    TagEasyunSecurityGroup = [{'ResourceType': 'security-group', 'Tags': TagEasyun}]

    logger.info('Entering applying security group' + data["securityGroup1"][0]['name'])
    secure_groupid = datacentersdk.add_VPC_security_group(ec2, vpc, data["securityGroup1"][0])
    logger.info('secure_group1= ' + secure_groupid)

    secure_groupid = datacentersdk.add_VPC_security_group(ec2, vpc, data["securityGroup2"][0])
    logger.info('secure_group1= ' + secure_groupid)

    secure_groupid = datacentersdk.add_VPC_security_group(ec2, vpc, data["securityGroup3"][0])
    logger.info('secure_group1= ' + secure_groupid)

    # secure_group1 = ec2.create_security_group(GroupName=sg, Description=sg_dict[sg], VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
    # ec2.authorize_security_group_ingress(
    #     GroupId=secure_group1['GroupId'],
    #     IpPermissions=IpPermissions1)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=3389, ToPort=3389)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='icmp', FromPort=-1, ToPort=-1)

    # create key pairs
    # TagEasyunKeyPair= [{'ResourceType':'key-pair','Tags': TagEasyun}]

    TagEasyunKeyPair = [
        {'ResourceType': 'key-pair',
         "Tags": [
             {"Key": "Flag", "Value": "Easyun"},
             {"Key": "Name", "Value": data['keypair']}
         ]
         }
    ]

    logger.info('Entering applying key pairs')

    try:
        new_keypair = vpc_resource.create_key_pair(KeyName=keypair, TagSpecifications=TagEasyunKeyPair, DryRun=DryRun)
        # keypair = 'key-easyun-user'
        if not os.path.exists('keys'):
            os.mkdir('keys')

        keypairfilename = keypair + '.pem'

        with open(os.path.join('./keys/', keypairfilename)) as file:
            file.write(new_keypair.key_material)
    except Exception as e:
        logger.info(e)
        return format_res(
            msg='Create key pairs failed due to already existed',
            code=2001
        )

    logger.info('create_vpc completion' + str(svc))
    # svc = {
    #     'region_name': REGION,
    #     'vpc_id': 'easyrun'
    # }
    return format_res(
        msg=svc,
        code=2001
    )

