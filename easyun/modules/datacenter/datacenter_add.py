# -*- coding: utf-8 -*-
"""
  @Description: DataCenter Management - action: start, restart, stop, delete; and get status
  @LastEditors: 
  @file:    datacenter_add.py
  @desc:    DataCenter Creation module
"""

from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String
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
from . import bp, bp, DC_REGION, DC_NAME, VERBOSE,IpPermissions1,IpPermissions2,IpPermissions3,secure_group1,secure_group2,secure_group3,TagEasyun,sg_dict,sg_ip_dict,keypair_filename,keypair_name,DryRun
from  .datacenter_sdk import datacentersdk,app_log

# from . import vpc_act

a = datacentersdk()
# 云服务器参数定义
NewDataCenter = {
    'region': 'us-east-2',
    'vpc_cidr' : '10.10.0.0/16',
    'pub_subnet1' : '192.168.1.0/24',
    'pub_subnet2' : '192.168.2.0/24',
    'pri_subnet1' : '192.168.3.0/24',
    'pri_subnet2' : '192.168.4.0/24',
    'key' : "key_easyun_dev",
    'secure_group1' : 'easyun-sg-default',
    'secure_group2' : 'easyun-sg-webapp',
    'secure_group3' : 'easyun-sg-database',
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

class DcParmIn(Schema):
    region = String(required=True, validate=Length(0, 20),
        example="us-east-1")     #VPC name
    vpc_cidr = String(required=True, validate=Length(0, 20),
        example="10.10.0.0/16")     #IP address range
    public_subnet_1 = String(required=True,
        example="10.10.1.0/24")
    public_subnet_2 = String(required=True,
        example="10.10.2.0/24")
    private_subnet_1 = String(required=True,
        example="10.10.11.0/24")
    private_subnet_2 = String(required=True,
        example="10.10.12.0/24")
    sgs1_flag = String(required=True,
        example="easyun-sg-default") 
    sgs2_flag = String(required=True,
        example="easyun-sg-webapp") 
    sgs3_flag = String(required=True,
        example="easyun-sg-database") 
    keypair = String(required=True,
        example="key_easyun_user")

class DcResultOut(Schema):
    region_name = String()
    vpc_id = String()

@bp.post('/add_dc')
@auth_required(auth_token)
@input(DcParmIn)
@output(DcResultOut, 201, description='add A new Datacenter')
def add_datacenter(data):
    '''新增 Datacenter
    curl -X 'POST' \
  'http://127.0.0.1:6660/api/v1/datacenter/add_dc' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer cYOaaQ1Xj6Ejdap0tYcLLZrHWExs42Ll' \
  -H 'Content-Type: application/json' \
  -d '{
  "keypair": "aaa",
  "private_subnet_1": "10.10.1.0/24",
  "private_subnet_2": "10.10.2.0/24",
  "public_subnet_1": "10.10.3.0/24",
  "public_subnet_2": "10.10.4.0/24",
  "region": "us-east-1",
  "sgs1_flag": "True",
  "sgs2_flag": "True",
  "sgs3_flag": "True",
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
    public_subnet_1 = data["public_subnet_1"]
    public_subnet_2 = data["public_subnet_2"]
    private_subnet_1 = data["private_subnet_1"]
    private_subnet_2 = data["private_subnet_2"]
    # sg_list= ['easyun-sg-default','easyun-sg-webapp','easyun-sg-database']
    sg_list=[]
    if data['sgs1_flag'] == 'True':
       sg_list.append('easyun-sg-default') 
    if data['sgs1_flag'] == 'True':
       sg_list.append('easyun-sg-webapp') 
    if data['sgs1_flag'] == 'True':
       sg_list.append('easyun-sg-database') 

    #a = datacentersdk()

    # print('haha'+str(sg_list))
    # logger.debug('haha'+str(sg_list))

    vpc_resource = boto3.resource('ec2', region_name=region)
    ec2 = boto3.client('ec2', region_name=region)
    # step 1: create VPC
    TagEasyunVPC= [{'ResourceType':'vpc','Tags': TagEasyun}]

    svc_list_resp = []
    # query account id from DB (only one account for both phase 1 and 2) ????
   
    try:
        vpc = vpc_resource.create_vpc(CidrBlock=vpc_cidr, TagSpecifications=TagEasyunVPC,DryRun=DryRun)
        print('VPC ID= '+ vpc.id )
        svc = {
        'region_name': DC_REGION,
        'vpc_id': vpc.id,
        }

        if datacentersdk.add_VPC_db(vpc.id,DC_REGION):
            current_app.logger.info('db operation is ok') 
        else:
            current_app.logger.info('db operation failed') 
            response = Result(detail ={'Result' : 'Errors'}, message='DB Insert failed', status_code=3001,http_status_code=400)
            current_app.logger.info(response.err_resp())
            response.err_resp()   


        svc_list_resp.append(svc)
        current_app.logger.info('create_vpc1' + str(svc_list_resp))
        # response = Result(detail = svc, status_code=3001)
        # print(response.make_resp())
        # return response.make_resp()
    except Exception:
        response = Result(detail ={'Result' : 'Errors'}, message='Datacenter VPC creation failed, maximum VPC reached', status_code=3001,http_status_code=400)
        current_app.logger.info(response.err_resp())
        response.err_resp()   
 


    # step 2: create Internet Gateway
    # Create and Attach the Internet Gateway
    TagEasyunIG= [{'ResourceType':'internet-gateway','Tags': TagEasyun}]
    try:
        igw = ec2.create_internet_gateway(TagSpecifications=TagEasyunIG,DryRun=DryRun)
        current_app.logger.info(f'Internet gateway created with: {json.dumps(igw, indent=4)}')
        vpc.attach_internet_gateway(InternetGatewayId=igw['InternetGateway']['InternetGatewayId'],DryRun=DryRun)
        current_app.logger.info('Internet Gateway ID= '+ igw['InternetGateway']['InternetGatewayId'])
    except Exception:
        response = Result(detail ={'Result' : 'Errors'}, message='Datacenter internet-gateway creation failed, maximum  reached', status_code=3001,http_status_code=400)
        current_app.logger.info(response.err_resp())
        response.err_resp()   

    # Create a route table and a public route to Internet Gateway
    TagEasyunRouteTable= [{'ResourceType':'route-table','Tags': TagEasyun}]

    route_table = vpc.create_route_table(TagSpecifications=TagEasyunRouteTable,DryRun=DryRun)
    route = route_table.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw['InternetGateway']['InternetGatewayId'],DryRun=DryRun
    )
    current_app.logger.info('Route Table ID= '+ route_table.id)

    # step 3: create 2 pub-subnet

    datacentersdk.add_subnet(ec2,vpc,route_table,public_subnet_1)
    datacentersdk.add_subnet(ec2,vpc,route_table,public_subnet_2)
    natSubnetId=datacentersdk.add_subnet(ec2,vpc,route_table,private_subnet_1)
    datacentersdk.add_subnet(ec2,vpc,route_table,private_subnet_2)


    # Create public Subnet1
    # TagEasyunSubnet= [{'ResourceType':'subnet','Tags': TagEasyun}]
    
    # pub_subnet1 = ec2.create_subnet(CidrBlock=public_subnet_1, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
    # print('Public subnet1= '+ pub_subnet1['Subnet']['SubnetId'])

    # # associate the route table with the subnet
    # route_table.associate_with_subnet(SubnetId=pub_subnet1['Subnet']['SubnetId'])

    # step 2: create NAT Gateway and allocate EIP
    # allocate IPV4 address for NAT gateway
    try:
        current_app.logger.info('Entering applying EIP')
        eip = ec2.allocate_address(Domain='vpc',DryRun=DryRun)
        current_app.logger.info(eip['PublicIp'])
        # create NAT gateway
        TagEasyunNATGateway= [{'ResourceType':'natgateway','Tags': TagEasyun}]
        
        current_app.logger.info('Entering applying NAT Gateway and it will take about 1 min, Be patient!!!')

        response = ec2.create_nat_gateway(
            AllocationId=eip['AllocationId'],
            SubnetId=natSubnetId,
            TagSpecifications=TagEasyunNATGateway,
            ConnectivityType='public',
            DryRun=DryRun)

        nat_gateway_id = response['NatGateway']['NatGatewayId']
        current_app.logger.info(nat_gateway_id)
        
        # wait until the NAT gateway is available
        waiter = ec2.get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[nat_gateway_id])
    except Exception:
        response = Result(detail ={'Result' : 'Errors'}, message='Datacenter VPC creation failed, maximum EIP/NAT reached', status_code=3001,http_status_code=400)
        current_app.logger.info(response.err_resp())
        response.err_resp()   

    # Step 5-1:  create security group easyun-sg-default
    # create security group allow SSH inbound rule through the VPC enable ssh/rdp/ping

    TagEasyunSecurityGroup= [{'ResourceType':'security-group','Tags': TagEasyun}]

    for sg in sg_list:
        current_app.logger.info('Entering applying security group'+sg)
        secure_groupid=datacentersdk.add_VPC_security_group(ec2,vpc,sg,sg_dict[sg],sg_ip_dict[sg])
        current_app.logger.info('secure_group1= '+secure_groupid)
    
    # secure_group1 = ec2.create_security_group(GroupName=sg, Description=sg_dict[sg], VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
    # ec2.authorize_security_group_ingress(
    #     GroupId=secure_group1['GroupId'],
    #     IpPermissions=IpPermissions1)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=3389, ToPort=3389)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='icmp', FromPort=-1, ToPort=-1)
    

    # create key pairs
    TagEasyunKeyPair= [{'ResourceType':'key-pair','Tags': TagEasyun}]
    
    current_app.logger.info('Entering applying key pairs')

    try:
        new_keypair = vpc_resource.create_key_pair(KeyName=keypair_name,TagSpecifications=TagEasyunKeyPair,DryRun=DryRun)
        # keypair_name = 'key-easyun-user'
        with open('./'+keypair_filename, 'w') as file:
            file.write(new_keypair.key_material)
    except Exception:
        response = Result(detail ={'Result' : 'Errors'}, message='Create key pairs failed due to already existed', status_code=3001,http_status_code=400)
        current_app.logger.info(response)

    # a.add_VPC_db(vpc,REGION)
    current_app.logger.info('create_vpc completion' + str(svc_list_resp))
    current_app.logger.info('create_vpc completion' + str(svc))
    # svc = {
    #     'region_name': REGION,
    #     'vpc_id': 'easyrun'
    # }
    response = Result(detail = svc, status_code=3001)
    return response.make_resp()

