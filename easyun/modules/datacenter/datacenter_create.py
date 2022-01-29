# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Creation
  @desc:    create some datacenter basic service, like vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

from apiflask import Schema, input, output, doc, abort, auth_required
from apiflask.fields import Integer, String, List, Dict, DateTime, Boolean
from apiflask.validators import Length, OneOf
from flask import current_app,jsonify
from datetime import date, datetime

from marshmallow.fields import Bool, Nested
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun import db, FLAG
import boto3
import os, time
import json
from . import bp, DC_REGION, DC_NAME, VERBOSE,TagEasyun,DryRun


# 定义Subnet参数的格式 (just for test)
class subNet(Schema):
    tagName = String(
        required=True,
        validate=Length(0, 40),
        example="Public subnet 1"
    )
    cidr = String(
        required=True,
        validate=Length(0, 20),
        example="10.11.1.0/24"
    )
    az = String(
        required=True,
        validate=Length(0, 20),
        example="us-east-1a"
    )    
    gateway = String(
        required=True,
        validate=Length(0, 20),
        example="easyun-igw"
    )
    routeTable = String(
        required=True,
        validate=Length(0, 30),
        example="easyun-rtb-igw"
    )
    # type = String(
    #     validate=OneOf(['public', 'private']),
    #     example="public"
    # )

# 定义Security Group参数的格式
class securityGroup(Schema):
    tagName = String(
        required=True,
        validate=Length(0, 20)
    )
    enablePing = Boolean(required=True, example=False)
    enableSSH = Boolean(required=True, example=False)
    enableRDP = Boolean(required=True, example=False)


# 定义api传入参数格式
class DcParmIn1(Schema):
    dcName = String(required=True, validate=Length(0, 60),
        example="Easyun")     #VPC name
    dcRegion = String(required=True, validate=Length(0, 20),
        example="us-east-1")             
    vpcCidr = String(required=True, validate=Length(0, 20),
        example="10.11.0.0/16")     #VPC IP address range
    
    pubSubnet1 = Nested(subNet, required=True,
        example={
            "tagName": "Public subnet 1",
            "az": "us-east-1b",
            "cidr": "10.11.1.0/24",
            "gateway": "easyun-igw",            
            "routeTable": "easyun-rtb-igw"
        }
    )
    pubSubnet2 = Nested(subNet, required=True,
        example={
            "tagName": "Public subnet 2",
            "az": "us-east-1c",
            "cidr": "10.11.2.0/24",
            "gateway": "easyun-igw",                
            "routeTable": "easyun-rtb-igw"
        }
    )
    priSubnet1 = Nested(subNet, required=True,
        example={
            "tagName": "Private subnet 1",
            "az": "us-east-1c",
            "cidr": "10.11.21.0/24",
            "gateway": "easyun-natgw",
            "routeTable": "easyun-rtb-nat"
        }
    )
    priSubnet2 = Nested(subNet, required=True,
        example={
            "tagName": "Private subnet 2",
            "az": "us-east-1c",
            "cidr": "10.11.22.0/24",
            "gateway": "easyun-natgw",                
            "routeTable": "easyun-rtb-nat"
        }
    )

    securityGroup0 = Nested(securityGroup, required=True,
        example={   
            "tagName": "easyun-sg-default",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        }
    )
    securityGroup1 = Nested(securityGroup, required=True,
        example={   
            "tagName": "easyun-sg-webapp",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        }
    )
    securityGroup2 = Nested(securityGroup, required=True,
        example={   
            "tagName": "easyun-sg-database",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        }
    )

# 定义api返回数据格式
class DcResultOut(Schema):
    name = String()
    region = String()
    vpc_id = String()
    create_date = DateTime()


@bp.post('/create')
@auth_required(auth_token)
@input(DcParmIn1)
@output(DcResultOut)
# @doc(tag='【仅限测试用】', operation_id='create_dc')
def create_dc(data):
    '''创建 Datacenter'''
    # Datacenter basic attribute difine
    dcName = data['dcName']
    dcRgeion = data['dcRegion']
    # Mandatory tag:Flag for all resource
    dcTag = {"Key": "Flag", "Value": dcName}
    
    resource_ec2 = boto3.resource('ec2', region_name = dcRgeion)
    client_ec2 = boto3.client('ec2', region_name = dcRgeion)

    # Step 0:  Check DC existed or not, if DC existed, need reject
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    if (thisDC is not None):
        response = Result(message='Datacenter already existed', status_code=2001,http_status_code=400)
        response.err_resp()   


    # Step 1: create easyun vpc, including:
    # 1* main route table
    # 1* default security group
    # 1* default Network ACLs
    try:
        nameTag = {"Key": "Name", "Value": "VPC-"+dcName}
        vpc = resource_ec2.create_vpc(
            CidrBlock= data['vpcCidr'],
            TagSpecifications = [
                {
                    'ResourceType':'vpc', 
                    "Tags": [dcTag, nameTag]
                }
            ]
        )
        stage = vpc.id+' created'
    except Exception as ex:
        resp = Result(detail=ex , status_code=2010)
        resp.err_resp()
        
    
    # step 2: create Internet Gateway
    try:
        nameTag = {"Key": "Name", "Value": data['pubSubnet1']['gateway']}
        igw = resource_ec2.create_internet_gateway(
            DryRun = DryRun,
            TagSpecifications = [
                {
                    'ResourceType':'internet-gateway', 
                    'Tags': [dcTag, nameTag]
                }
            ]
        )
        # waiter = client_ec2.get_waiter('internet_gateway_exists')
        # waiter.wait(InternetGatewayIds=[igw.id])   
        # got Error：ValueError: Waiter does not exist: internet_gateway_exists 
        stage = igw.id+' created'

        # and Attach the igw to vpc
        igw.attach_to_vpc(
            DryRun = DryRun,
            VpcId = vpc.id
        )
        stage = igw.id+" attached to "+vpc.id

    except Exception as ex:
        resp = Result(detail=ex , status_code=2020)
        resp.err_resp()


    # step 3: create 2x Public Subnets
    try:
        nameTag = {"Key": "Name", "Value": data['pubSubnet1']['tagName']}
        pubsbn1 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= data['pubSubnet1']['cidr'],
            AvailabilityZone = data['pubSubnet1']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [dcTag, nameTag]
                }
            ]
        )
        stage = pubsbn1.id+' created'
        
        nameTag = {"Key": "Name", "Value": data['pubSubnet2']['tagName']}
        pubsbn2 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= data['pubSubnet2']['cidr'],
            AvailabilityZone = data['pubSubnet2']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [dcTag, nameTag]
                }
            ]
        )
        stage = pubsbn2.id+' created'
        
    except Exception as ex:
        resp = Result(detail=ex , status_code=2030)
        resp.err_resp()


    # step 4: update main route table （route-igw）
    try:
        nameTag = {"Key": "Name", "Value": data['pubSubnet1']['routeTable']}
        rtbs = vpc.route_tables.all()
        for rtb in rtbs:
            if rtb.associations_attribute[0]['Main']:  
                #添加tag:Name
                rtb.create_tags(
                    DryRun=DryRun,
                    Tags=[dcTag, nameTag]
                )
                print(rtb.tags)
                
                #添加到 igw的路由
                irt = rtb.create_route(
                    DryRun=DryRun,
                    DestinationCidrBlock='0.0.0.0/0',            
                    GatewayId= igw.id
        #             NatGatewayId='string',
        #             NetworkInterfaceId='string',
                )
                stage = irt.destination_cidr_block+' created'
                
                #associate the route table with the pub subnets
                rtba1 = rtb.associate_with_subnet(
                    DryRun= DryRun,
                    SubnetId= pubsbn1.id            
                )

                rtba2 = rtb.associate_with_subnet(
                    DryRun= DryRun,
                    SubnetId= pubsbn2.id,
                )

    except Exception as ex:
        resp = Result(detail=ex , status_code=2040)
        resp.err_resp()


    # step 5: create 2x Private Subnets
    try:
        nameTag = {"Key": "Name", "Value": data['priSubnet1']['tagName']}
        prisbn1 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= data['priSubnet1']['cidr'],
            AvailabilityZone = data['priSubnet1']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [dcTag, nameTag]
                }
            ]
        )
        stage = prisbn1.id+' created'
        
        nameTag = {"Key": "Name", "Value": data['priSubnet2']['tagName']}
        prisbn2 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= data['priSubnet2']['cidr'],
            AvailabilityZone = data['priSubnet2']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [dcTag, nameTag]
                }
            ]
        )
        stage = prisbn2.id+' created'
        
    except Exception as ex:
        resp = Result(detail=ex , status_code=2050)
        resp.err_resp()


    # step 6: create NAT Gateway with EIP

    # 6-1: Allocate EIP for NAT Gateway
    try:
        nameTag = {"Key": "Name", "Value": dcName.lower()+"natgw-eip"}
        eip = client_ec2.allocate_address(
            DryRun=DryRun,
            Domain='vpc',
            TagSpecifications = [
                {
                    'ResourceType':'elastic-ip', 
                    "Tags": [dcTag, nameTag]
                }
            ]
        )
        stage = eip['PublicIp']+' created'
  
    except Exception as ex:
        resp = Result(detail=ex , status_code=2061)
        resp.err_resp()

    # 6-2: create nat gateway
    try:
        nameTag = {"Key": "Name", "Value": data['priSubnet1']['gateway']}
        natgw = client_ec2.create_nat_gateway(
            DryRun = DryRun,
            ConnectivityType='public',
            AllocationId=eip['AllocationId'],
            SubnetId = pubsbn1.id,
            TagSpecifications = [
                {
                    'ResourceType':'natgateway', 
                    "Tags": [dcTag, nameTag]
                }
            ]
        )
        natgwID = natgw['NatGateway']['NatGatewayId']
        stage = natgwID+' creating'

        # waite natgw created
        try:    
            waiter = client_ec2.get_waiter('nat_gateway_available')
            waiter.wait(NatGatewayIds=[natgwID])            
            stage = natgwID+' created'
        except Exception as ex:
            resp = Result(detail=ex , status_code=2062)
            resp.err_resp()

    except Exception as ex:
        resp = Result(detail=ex , status_code=2060)
        resp.err_resp()


    # step 7: create NAT route table and route to natgw
    # 7-1 create route table for natgw
    try:
        nameTag = {"Key": "Name", "Value": data['priSubnet1']['routeTable']}
        nrtb = vpc.create_route_table(
            DryRun=DryRun,
            TagSpecifications=[
                {
                    'ResourceType':'route-table', 
                    "Tags": [dcTag, nameTag]
                }
            ]
        )

        # add a route to natgw
        nrt = nrtb.create_route(
            DryRun=DryRun,
            DestinationCidrBlock='0.0.0.0/0',            
            # GatewayId= igw.id,
            NatGatewayId= natgwID
#             NetworkInterfaceId='string',        
        )
        stage = nrt.destination_cidr_block+' created'

        # associate the route table with the pri subnets
        rtba3 = nrtb.associate_with_subnet(
            DryRun= DryRun,
            SubnetId= prisbn1.id            
        )
        rtba4 = nrtb.associate_with_subnet(
            DryRun= DryRun,
            SubnetId= prisbn2.id,
        )

    except Exception as ex:
        resp = Result(detail=ex , status_code=2070)
        resp.err_resp()


    # step 8: update and create Security Groups
    webPerm = [
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
    dbPerm = [
        {
            'IpProtocol': 'tcp',
            'FromPort': 3306,
            'ToPort': 3306,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 5432,
            'ToPort': 5432,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 1521,
            'ToPort': 1521,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 1443,
            'ToPort': 1443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },                
    ]

    # 8-1: update default security group
    try:
        nameTag = {"Key": "Name", "Value": data['securityGroup0']['tagName']}
        basePerm = check_perm(data['securityGroup0'])
        for sg in vpc.security_groups.all():
            if sg.group_name == 'default':
                #添加tag:Name
                sg.create_tags(
                    DryRun=DryRun,
                    Tags=[dcTag, nameTag]
                )
                #更新default sg inbound规则
                sg.authorize_ingress(
                    DryRun=DryRun,
                    IpPermissions= basePerm,                
                )
    except Exception as ex:
        resp = Result(detail=ex , status_code=2081)
        resp.err_resp()

    # 8-2: create webapp security group
    try:
        nameTag = {"Key": "Name", "Value": data['securityGroup1']['tagName']}
        basePerm = check_perm(data['securityGroup1'])
        sgWeb = resource_ec2.create_security_group(
            DryRun=DryRun,
            GroupName=nameTag['Value'],
            Description='allow http access to web server',
            VpcId=vpc.id,
            TagSpecifications = [ 
                {'ResourceType':'security-group', 
                "Tags": [dcTag, nameTag]
                }
            ]
        )
        #更新sgWeb inbound规则
        webPerm.extend(basePerm)
        sgWeb.authorize_ingress(
            DryRun=DryRun,
    #         SourceSecurityGroupName='string',
    #         SourceSecurityGroupOwnerId='string'
            IpPermissions= webPerm
        )
    except Exception as ex:
        resp = Result(detail=ex , status_code=2082)
        resp.err_resp()

    # 8-3: create database security group
    try:
        nameTag = {"Key": "Name", "Value": data['securityGroup2']['tagName']}
        basePerm = check_perm(data['securityGroup2'])
        sgDb = resource_ec2.create_security_group(
            DryRun=DryRun,
            GroupName=nameTag['Value'],
            Description='allow tcp access to db server',
            VpcId=vpc.id,
            TagSpecifications = [ 
                {'ResourceType':'security-group', 
                "Tags": [dcTag, nameTag]
                }
            ]
        )
        #更新sgWeb inbound规则
        dbPerm.extend(basePerm)
        sgDb.authorize_ingress(
            DryRun=DryRun,
    #         SourceSecurityGroupName='string',
    #         SourceSecurityGroupOwnerId='string'
            IpPermissions= dbPerm
        )
    except Exception as ex:
        resp = Result(detail=ex , status_code=2083)
        resp.err_resp()


   # step 9: Write Datacenter metadata to local database
    try:
        curr_account:Account = Account.query.first()
        curr_user = auth_token.current_user.username
        # curr_user = 'test-user'
        newDC = Datacenter(
            name=dcName,
            cloud='AWS', 
            account_id = curr_account.account_id, 
            region = dcRgeion,
            vpc_id = vpc.id,
            create_date = datetime.utcnow(),
            create_user = curr_user
        )
        db.session.add(newDC)
        db.session.commit()

        resp = Result(
            detail = newDC,
            status_code = 200 
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(detail=ex , status_code=2092)
        resp.err_resp()

# step 10: Update Datacenter name list to DynamoDB
    try:
        # 待補充
        resp = Result(
            detail = 'updated.',
            status_code = 200 
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(detail=ex , status_code=2092)
        resp.err_resp()


# 根據勾選狀態匹配Security group IP規則
def check_perm(sg):
    permList = []
    if sg["enableRDP"]:
        permList.append({
            'IpProtocol': 'tcp',
            'FromPort': 3389,
            'ToPort': 3389,
#             'Ipv6Ranges': [], 
#             'PrefixListIds': [], 
#             'UserIdGroupPairs': [],            
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        })

    if sg["enableSSH"]:
        permList.append({
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
#             'Ipv6Ranges': [], 
#             'PrefixListIds': [], 
#             'UserIdGroupPairs': [],            
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        })

    if sg["enablePing"]:
        permList.append({
            'IpProtocol': 'icmp',
            'FromPort': 8,
            'ToPort': -1,
#             'Ipv6Ranges': [], 
#             'PrefixListIds': [], 
#             'UserIdGroupPairs': [],            
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        })
    return permList