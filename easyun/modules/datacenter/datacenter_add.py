# -*- coding: utf-8 -*-
"""
  @author:  pengchang
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited. 
  @file:    datacenter_add.py
  @desc:    The DataCenter Create module
"""

from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import jsonify
from datetime import date, datetime
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun import db
import boto3
import os, time
import json
from . import bp, REGION, FLAG, VERBOSE,IpPermissions1,IpPermissions2,IpPermissions3,secure_group1,secure_group2,secure_group3,TagEasyun
from . import datacentersdk

# from . import vpc_act


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
                {"Key": "Flag", "Value": FLAG},
                {"Key": "Name", "Value": 'test-from-api'}
            ]
        }
        ]
}

def add_subnet(ec2,vpc,route_table,subnet):
            TagEasyunSubnet= [{'ResourceType':'subnet','Tags': TagEasyun}]

            subnet = ec2.create_subnet(CidrBlock=subnet, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
            # associate the route table with the subnet
            route_table.associate_with_subnet(SubnetId=subnet['Subnet']['SubnetId'])
            print('Public subnet1= '+ subnet['Subnet']['SubnetId'])


def add_VPC_security_group(ec2,vpc,groupname,description,IpPermissions):
    TagEasyunSecurityGroup= [{'ResourceType':'security-group','Tags': TagEasyun}]
    
    secure_group = ec2.create_security_group(GroupName=groupname, Description=description, VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
    
    ec2.authorize_security_group_ingress(
        GroupId=secure_group['GroupId'],
        IpPermissions=IpPermissions)
    
    print('secure_group2= '+secure_group['GroupId'])


def add_VPC_db(vpc,region):
    new_datacenter = Datacenter(id=1,name='Easyun',cloud='AWS', account='', region=region,vpc_id=vpc.id,credate=datetime.date())
    db.session.add(new_datacenter)
        


class AddDatacenter(Schema):
    region = String(required=True, validate=Length(0, 20))     #VPC name
    vpc_cidr = String(required=True, validate=Length(0, 20))     #IP address range
    public_subnet_1 = String(required=True)
    public_subnet_2 = String(required=True)
    private_subnet_1 = String(required=True)
    private_subnet_2 = String(required=True)
    sgs1_flag = String(required=True) 
    sgs2_flag = String(required=True) 
    sgs3_flag = String(required=True) 
    keypair = String(required=True)


@bp.post('/add_dc')
@auth_required(auth_token)
@input(AddDatacenter)
@output({}, 201, description='add A new Datacenter')
def add_datacenter(data):
    '''新增 Datacenter'''
    # create easyun vpc
    # create 2 x pub-subnet
    # create 2 x pri-subnet
    # create 1 x easyun-igw (internet gateway)
    # create 1 x easyun-nat (nat gateway)
    # create 1 x easyun-route-igw
    # create 1 x easyun-route-nat
    # create 3 x easyun-sg-xxx
    # create 1 x key-easyun-user (默认keypair)
    print(data)
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
    print('haha'+str(sg_list))

    vpc_resource = boto3.resource('ec2', region_name=region)
    ec2 = boto3.client('ec2', region_name=region)
    # step 1: create VPC
    TagEasyunVPC= [{'ResourceType':'vpc','Tags': TagEasyun}]

    list_resp = []

    try:
        vpc = vpc_resource.create_vpc(CidrBlock=vpc_cidr, TagSpecifications=TagEasyunVPC)
        print('VPC ID= '+ vpc.id )
        svc = {
        'region': REGION,
        'vpc_id': vpc.id,
        }

        list_resp.append(svc)
        print('haha' + str(list_resp))

        response = Result(detail = list_resp, status_code=3001)

        print(response.make_resp())
        return response.make_resp()

    except Exception:
        response = Result(message='Datacenter VPC creation failed, maximum VPC reached', status_code=3001,http_status_code=400)
        response.err_resp()   
         


    # step 2: create Internet Gateway
    # Create and Attach the Internet Gateway
    TagEasyunIG= [{'ResourceType':'internet-gateway','Tags': TagEasyun}]

    igw = ec2.create_internet_gateway(TagSpecifications=TagEasyunIG)
    print(f'Internet gateway created with: {json.dumps(igw, indent=4)}')
    vpc.attach_internet_gateway(InternetGatewayId=igw['InternetGateway']['InternetGatewayId'])
    print('Internet Gateway ID= '+ igw['InternetGateway']['InternetGatewayId'])

    # Create a route table and a public route to Internet Gateway
    TagEasyunRouteTable= [{'ResourceType':'route-table','Tags': TagEasyun}]

    route_table = vpc.create_route_table(TagSpecifications=TagEasyunRouteTable)
    route = route_table.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw['InternetGateway']['InternetGatewayId']

    )
    print('Route Table ID= '+ route_table.id)

    # step 3: create 2 pub-subnet

    add_subnet(ec2,vpc,route_table,public_subnet_1)
    add_subnet(ec2,vpc,route_table,public_subnet_2)
    add_subnet(ec2,vpc,route_table,private_subnet_1)
    add_subnet(ec2,vpc,route_table,private_subnet_2)


    # Create public Subnet1
    TagEasyunSubnet= [{'ResourceType':'subnet','Tags': TagEasyun}]
    
    pub_subnet1 = ec2.create_subnet(CidrBlock=public_subnet_1, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
    print('Public subnet1= '+ pub_subnet1['Subnet']['SubnetId'])

    # associate the route table with the subnet
    route_table.associate_with_subnet(SubnetId=pub_subnet1['Subnet']['SubnetId'])

    # Create public Subnet2
    pub_subnet2 = ec2.create_subnet(CidrBlock=public_subnet_2, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
    print('Public subnet2= '+pub_subnet2['Subnet']['SubnetId'])

    # associate the route table with the subnet
    route_table.associate_with_subnet(SubnetId=pub_subnet2['Subnet']['SubnetId'])

    # step 3: create 2 private-subnet
    # Create private Subnet1
    private_subnet1 = ec2.create_subnet(CidrBlock=private_subnet_1, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
    print('Private subnet1= '+private_subnet1['Subnet']['SubnetId'])

    # associate the route table with the subnet
    route_table.associate_with_subnet(SubnetId=private_subnet1['Subnet']['SubnetId'])

    # Create private Subnet2
    private_subnet2 = ec2.create_subnet(CidrBlock=private_subnet_2, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
    print('Private subnet2= '+private_subnet2['Subnet']['SubnetId'])

    # associate the route table with the subnet
    route_table.associate_with_subnet(SubnetId=private_subnet2['Subnet']['SubnetId'])

    # step 2: create NAT Gateway and allocate EIP
    # allocate IPV4 address for NAT gateway
    eip = ec2.allocate_address(Domain='vpc')
    print(eip)
    # create NAT gateway
    TagEasyunNATGateway= [{'ResourceType':'natgateway','Tags': TagEasyun}]

    response = ec2.create_nat_gateway(
        AllocationId=eip['AllocationId'],
        SubnetId=private_subnet1['Subnet']['SubnetId'],
        TagSpecifications=TagEasyunNATGateway,
        ConnectivityType='public')
    nat_gateway_id = response['NatGateway']['NatGatewayId']

    # wait until the NAT gateway is available
    waiter = ec2.get_waiter('nat_gateway_available')
    waiter.wait(NatGatewayIds=[nat_gateway_id])

    # eip = ec2.allocate_address(Domain='vpc')
    #
    # # Create and Attach the NAT Gateway
    # nat_gatway = ec2.create_nat_gateway(SubnetId=private_subnet1['Subnet']['SubnetId'],AllocationId=eip['AllocationId'],TagSpecifications=[{
    #                                             'ResourceType':'natgateway',
    #                                             'Tags': [{
    #                                                 'Key':'FLAG',
    #                                                 'Value':'easyun'
    #                                             }]
    #                                                 }])
    # nat_gateway_id = nat_gatway['NatGateway']['NatGatewayId']
    # print('NAT gateway id= '+nat_gateway_id)

            # wait until the NAT gateway is available
    # waiter = client1.get_waiter('nat_gateway_available')
    # waiter.wait(nat_gateway_id)

    #print(nat_gateway_id)

    # Step 5-1:  create security group easyun-sg-default
    # create security group allow SSH inbound rule through the VPC enable ssh/rdp/ping
    # 

    TagEasyunSecurityGroup= [{'ResourceType':'security-group','Tags': TagEasyun}]

    for sg in sg_list:
        secure_group1 = ec2.create_security_group(GroupName=sg, Description='Secure Group For Default', VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
        ec2.authorize_security_group_ingress(
            GroupId=secure_group1['GroupId'],
            IpPermissions=IpPermissions1)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=3389, ToPort=3389)
    # secure_group1.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='icmp', FromPort=-1, ToPort=-1)
        print('secure_group1= '+secure_group1['GroupId'])

    # Step 5-2:  create security group easyun-sg-webapp

    secure_group2 = ec2.create_security_group(GroupName='easyun-sg-webapp', Description='Secure Group For Webapp', VpcId=vpc.id,
                                            TagSpecifications=TagEasyunSecurityGroup)
    # secure_group2.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=80)
    # secure_group2.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=443)

    ec2.authorize_security_group_ingress(
    GroupId=secure_group2['GroupId'],
    IpPermissions=IpPermissions2)

    print('secure_group2= '+secure_group2['GroupId'])

    # Step 5-3:  create security group easyun-sg-database

    secure_group3 = ec2.create_security_group(GroupName='easyun-sg-database', Description='Secure Group For Database', VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
    # secure_group3.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=3306)
    # secure_group3.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=5432)
    # secure_group3.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=1521)
    # secure_group3.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=1443)
    
    ec2.authorize_security_group_ingress(
        GroupId=secure_group3['GroupId'],
        IpPermissions=IpPermissions3)
    
   
    # add_VPC_security_group(ec2,'easyun-sg-default','Secure Group For default',vpc,IpPermissions1);
    # add_VPC_security_group(ec2,'easyun-sg-webapp','Secure Group For webapp',vpc,IpPermissions2);
    # add_VPC_security_group(ec2,'easyun-sg-database','Secure Group For database',vpc,IpPermissions3);

    print('secure_group3= '+secure_group3['GroupId'])

    # create key pairs
    TagEasyunKeyPair= [{'ResourceType':'key-pair','Tags': TagEasyun}]

    response = ec2.create_key_pair(KeyName='key-easyun-user',TagSpecifications=TagEasyunKeyPair)
    print(response)

    add_VPC_db(vpc,REGION)

    response = Result(
        # detail = servers,
        detail=[{
            'VPC ID' : vpc.id,
        }] ,
        status_code=3001
    )
        # server = [{'id':'3131442142'}]
        # response = Result(
        #     detail={'NewSvrId':server[0]['id']}, status_code=3001
        # )

    return response.make_resp()





class VpcListIn(Schema):
    vpc_id = String()


class VpcListOut(Schema):
    vpc_id = String()
    pub_subnet1 = String() 
    pub_subnet2 = String() 
    private_subnet1 = String() 
    private_subnet2 = String() 
    sgs = String() 
    keypair = String()


@bp.get('/dc_info')
@auth_required(auth_token)
@input(VpcListIn)
@output(VpcListOut, description='Get Datacenter info')
def get_vpc(vpc_id):
    '''获取当前Datacenter资源信息'''
    # get vpc info
    # get subnet info
    # get securitygroup info
    # get keypair info

    ec2 = boto3.resource('ec2', region_name=REGION)
    vpcs = ec2.describer_vpcs( VpcIds=[
        'VpcListIn',
    ],
    Filters=[
        {'Name': 'tag:Flag','Values': [FLAG]}
    ])
    vpclist = {}
    print(json.dumps(vpcs, sort_keys=True, indent=4))

    return jsonify(vpcs)
    
    return '' #datacenter id



@bp.post('/cleanup')
@auth_token.login_required
@input({})
@output({}, 201, description='Remove the Datacenter')
def remove_datacenter(this_dc):
    '''删除Datacenter'''
    # delete easyun vpc
    # delete 2 x pub-subnet
    # delete 2 x pri-subnet
    # delete 1 x easyun-igw (internet gateway)
    # delete 1 x easyun-nat (nat gateway)
    # delete 1 x easyun-route-igw
    # delete 1 x easyun-route-nat
    # delete 3 x easyun-sg-xxx
    # delete 1 x key-easyun-user (默认keypair)
    try:
        ec2 = boto3.resource('ec2', region_name=REGION)
        vpc_id = ec2.describer_vpcs( VpcIds='vpc_id',
    Filters=[
        {'Name': 'tag:Flag','Values': [FLAG]}
    ])
      
    except  boto3.exceptions.Boto3Error as e:
      print(e)
      exit(1)
    else:
       del_igw(ec2, vpc_id)
       del_sub(ec2, vpc_id)
       del_rtb(ec2, vpc_id)
       del_acl(ec2, vpc_id)
       del_sgp(ec2, vpc_id)
       del_vpc(ec2, vpc_id)
        
def get_regions(client):
    """ Build a region list """

    reg_list = []
    regions = client.describe_regions()
    data_str = json.dumps(regions)
    resp = json.loads(data_str)
    region_str = json.dumps(resp['Regions'])
    region = json.loads(region_str)
    for reg in region:
        reg_list.append(reg['RegionName'])
    return reg_list

def get_default_vpcs(client):
    vpc_list = []
    vpcs = client.describe_vpcs(
        Filters=[
        {
            'Name' : 'isDefault',
            'Values' : [
                'true',
            ],
        },
        ]
    )
    vpcs_str = json.dumps(vpcs)
    resp = json.loads(vpcs_str)
    data = json.dumps(resp['Vpcs'])
    vpcs = json.loads(data)

    for vpc in vpcs:
        vpc_list.append(vpc['VpcId'])  

    return vpc_list

def del_igw(ec2, vpcid):
    """ Detach and delete the internet-gateway """
    vpc_resource = ec2.Vpc(vpcid)
    igws = vpc_resource.internet_gateways.all()
    if igws:
        for igw in igws:
            try:
                print("Detaching and Removing igw-id: ", igw.id) if (VERBOSE == 1) else ""
                igw.detach_from_vpc(
                VpcId=vpcid
                )
                igw.delete(# DryRun=True
                )
            except boto3.exceptions.Boto3Error as e:
                print(e)

def del_sub(ec2, vpcid):
    """ Delete the subnets """
    vpc_resource = ec2.Vpc(vpcid)
    subnets = vpc_resource.subnets.all()
    default_subnets = [ec2.Subnet(subnet.id) for subnet in subnets if subnet.default_for_az]

    if default_subnets:
        try:
            for sub in default_subnets: 
                print("Removing sub-id: ", sub.id) if (VERBOSE == 1) else ""
                sub.delete(
                # DryRun=True
                )
        except boto3.exceptions.Boto3Error as e:
            print(e)

def del_rtb(ec2, vpcid):
    """ Delete the route-tables """
    vpc_resource = ec2.Vpc(vpcid)
    rtbs = vpc_resource.route_tables.all()
    if rtbs:
        try:
            for rtb in rtbs:
                assoc_attr = [rtb.associations_attribute for rtb in rtbs]
                if [rtb_ass[0]['RouteTableId'] for rtb_ass in assoc_attr if rtb_ass[0]['Main'] == True]:
                    print(rtb.id + " is the main route table, continue...")
                    continue
                    print("Removing rtb-id: ", rtb.id) if (VERBOSE == 1) else ""
                    table = ec2.RouteTable(rtb.id)
                    table.delete(
                    # DryRun=True
                    )
        except boto3.exceptions.Boto3Error as e:
            print(e)

def del_acl(ec2, vpcid):
    """ Delete the network-access-lists """

    vpc_resource = ec2.Vpc(vpcid)      
    acls = vpc_resource.network_acls.all()

    if acls:
        try:
            for acl in acls: 
                if acl.is_default:
                    print(acl.id + " is the default NACL, continue...")
                    continue
                    print("Removing acl-id: ", acl.id) if (VERBOSE == 1) else ""
                    acl.delete(
                    # DryRun=True
                    )
        except boto3.exceptions.Boto3Error as e:
            print(e)

def del_sgp(ec2, vpcid):
    """ Delete any security-groups """
    vpc_resource = ec2.Vpc(vpcid)
    sgps = vpc_resource.security_groups.all()
    if sgps:
        try:
            for sg in sgps: 
                if sg.group_name == 'default':
                    print(sg.id + " is the default security group, continue...")
                    continue
                    print("Removing sg-id: ", sg.id) if (VERBOSE == 1) else ""
                    sg.delete(
                    # DryRun=True
                    )
        except boto3.exceptions.Boto3Error as e:
            print(e)

def del_vpc(ec2, vpcid):
    """ Delete the VPC """
    vpc_resource = ec2.Vpc(vpcid)
    try:
        print("Removing vpc-id: ", vpc_resource.id)
        vpc_resource.delete(
        # DryRun=True
        )
    except boto3.exceptions.Boto3Error as e:
        print(e)
        print("Please remove dependencies and delete VPC manually.")
    #finally:



  #  return status