# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Creation
  @desc:    create some datacenter basic service, like vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

import imp
import boto3
import os, time
from datetime import date, datetime
from flask import current_app,jsonify, request
from apiflask import Schema, input, output, doc, abort, auth_required
from apiflask.fields import Integer, String, List, Dict, DateTime, Boolean
from apiflask.validators import Length, OneOf
from celery.result import ResultBase, AsyncResult
from easyun import db, log, celery
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.utils import gen_dc_tag
from easyun.common.result import Result, make_resp, error_resp, bad_request
from .schemas import CreateDcParms, CreateDcResult
from . import bp, DC_REGION, DC_NAME, DryRun


logger = log.create_logger('dcm')

@bp.post('')
@auth_required(auth_token)
@input(CreateDcParms)
@output(CreateDcResult)
@log.api_logger(logger)
def create_dc_sync(parm):
    '''创建 Datacenter 及基础资源'''
    newDc = create_dc_task.apply_async(args=[parm, ])
    resp = Result(
        detail=newDc, 
        status_code=200
    )
    return resp.make_resp()


@bp.get('/result')
@auth_required(auth_token)
def fetch_task_state():
    '''获取创建 Datacenter 任务执行状态'''
    request_id = request.args.get('id')
    task = AsyncResult(request_id, app=celery)
    if task.ready():
        state = task.result
        return Result(
            detail=state.get('msg'),
            status_code=state.get('code')
        ).make_resp()
    else:
        return Result(
            detail='Creating ...',
            status_code=2000
        ).make_resp()


@celery.task()
def create_dc_task(parm):
    '''创建 Datacenter 异步任务
    :return {msg: code: http_code:默认200}    
    '''
    
    # Datacenter basic attribute difine
    dcName = parm['dcName']
    dcRgeion = parm['dcRegion']
    # Mandatory tag:Flag for all resource
    flagTag = gen_dc_tag(dcName)
    
    resource_ec2 = boto3.resource('ec2', region_name = dcRgeion)
    client_ec2 = boto3.client('ec2', region_name = dcRgeion)

    # Step 0:  Check DC existed or not, if DC existed, need reject
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    if (thisDC is not None):
        resp = Result(
            message='Datacenter already existed',
            status_code=2001,
            http_status_code=400
        )
        resp.err_resp()   


    # Step 1: create easyun vpc, including:
    # 1* main route table
    # 1* default security group
    # 1* default Network ACLs
    try:
        nameTag = {"Key": "Name", "Value": "VPC-"+dcName}
        vpc = resource_ec2.create_vpc(
            CidrBlock= parm['cidrBlock'],
            TagSpecifications = [
                {
                    'ResourceType':'vpc', 
                    "Tags": [flagTag, nameTag]
                }
            ]
        )
        stage = vpc.id+' created'
        logger.info(stage)
    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2010)
        resp.err_resp()
        
    
    # step 2: create Internet Gateway
    try:
        nameTag = {"Key": "Name", "Value": parm['pubSubnet1']['gateway']}
        igw = resource_ec2.create_internet_gateway(
            DryRun = DryRun,
            TagSpecifications = [
                {
                    'ResourceType':'internet-gateway', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        # waiter = client_ec2.get_waiter('internet_gateway_exists')
        # waiter.wait(InternetGatewayIds=[igw.id])   
        # got Error：ValueError: Waiter does not exist: internet_gateway_exists 
        stage = igw.id+' created'
        logger.info(stage)

        # and Attach the igw to vpc
        igw.attach_to_vpc(
            DryRun = DryRun,
            VpcId = vpc.id
        )
        stage = igw.id+" attached to "+vpc.id
        logger.info(stage)

    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2020)
        resp.err_resp()


    # step 3: create 2x Public Subnets
    try:
        nameTag = {"Key": "Name", "Value": parm['pubSubnet1']['tagName']}
        pubsbn1 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['pubSubnet1']['cidr'],
            AvailabilityZone = parm['pubSubnet1']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = pubsbn1.id+' created'
        logger.info(stage)
        
        nameTag = {"Key": "Name", "Value": parm['pubSubnet2']['tagName']}
        pubsbn2 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['pubSubnet2']['cidr'],
            AvailabilityZone = parm['pubSubnet2']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = pubsbn2.id+' created'
        logger.info(stage)
        
    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2030)
        resp.err_resp()


    # step 4: update main route table （route-igw）
    try:
        nameTag = {"Key": "Name", "Value": parm['pubSubnet1']['routeTable']}
        rtbs = vpc.route_tables.all()
        for rtb in rtbs:
            if rtb.associations_attribute[0]['Main']:  
                #添加tag:Name
                rtb.create_tags(
                    DryRun=DryRun,
                    Tags=[flagTag, nameTag]
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
                logger.info(stage)
                
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
        resp = Result(detail=str(ex) , status_code=2040)
        resp.err_resp()


    # step 5: create 2x Private Subnets
    try:
        nameTag = {"Key": "Name", "Value": parm['priSubnet1']['tagName']}
        prisbn1 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['priSubnet1']['cidr'],
            AvailabilityZone = parm['priSubnet1']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = prisbn1.id+' created'
        logger.info(stage)
        
        nameTag = {"Key": "Name", "Value": parm['priSubnet2']['tagName']}
        prisbn2 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['priSubnet2']['cidr'],
            AvailabilityZone = parm['priSubnet2']['az'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = prisbn2.id+' created'
        logger.info(stage)
        
    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2050)
        resp.err_resp()


    # step 6: create NAT Gateway with EIP
    # 6-1: Allocate EIP for NAT Gateway
    try:
        nameTag = {"Key": "Name", "Value": dcName.lower()+"natgw-eip"}
        eip = client_ec2.allocate_address(
        # eip = resource_ec2.meta.client.allocate_address(
            DryRun=DryRun,
            Domain='vpc',
            TagSpecifications = [
                {
                    'ResourceType':'elastic-ip', 
                    "Tags": [flagTag, nameTag]
                }
            ]
        )
        stage = eip['PublicIp']+' created'
        logger.info(stage)
  
    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2061)
        resp.err_resp()

    # 6-2: create nat gateway
    try:
        nameTag = {"Key": "Name", "Value": parm['priSubnet1']['gateway']}
        natgw = client_ec2.create_nat_gateway(
            DryRun = DryRun,
            ConnectivityType='public',
            AllocationId=eip['AllocationId'],
            SubnetId = pubsbn1.id,
            TagSpecifications = [
                {
                    'ResourceType':'natgateway', 
                    "Tags": [flagTag, nameTag]
                }
            ]
        )
        natgwID = natgw['NatGateway']['NatGatewayId']
        stage = natgwID+' creating'
        logger.info(stage)

        # waite natgw created
        try:    
            waiter = client_ec2.get_waiter('nat_gateway_available')
            waiter.wait(NatGatewayIds=[natgwID])            
            stage = natgwID+' created'
            logger.info(stage)
        except Exception as ex:
            resp = Result(detail=str(ex) , status_code=2062)
            resp.err_resp()

    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2060)
        resp.err_resp()


    # step 7: create NAT route table and route to natgw
    # 7-1 create route table for natgw
    try:
        nameTag = {"Key": "Name", "Value": parm['priSubnet1']['routeTable']}
        nrtb = vpc.create_route_table(
            DryRun=DryRun,
            TagSpecifications=[
                {
                    'ResourceType':'route-table', 
                    "Tags": [flagTag, nameTag]
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
        logger.info(stage)

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
        resp = Result(detail=str(ex) , status_code=2070)
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
        nameTag = {"Key": "Name", "Value": parm['securityGroup0']['tagName']}
        basePerm = check_perm(parm['securityGroup0'])
        for sg in vpc.security_groups.all():
            if sg.group_name == 'default':
                #添加tag:Name
                sg.create_tags(
                    DryRun=DryRun,
                    Tags=[flagTag, nameTag]
                )
                #更新default sg inbound规则
                sg.authorize_ingress(
                    DryRun=DryRun,
                    IpPermissions= basePerm,                
                )
                break
        stage = sg.group_name+' updated'
        logger.info(stage)

    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2081)
        resp.err_resp()

    # 8-2: create webapp security group
    try:
        nameTag = {"Key": "Name", "Value": parm['securityGroup1']['tagName']}
        basePerm = check_perm(parm['securityGroup1'])
        sgWeb = resource_ec2.create_security_group(
            DryRun=DryRun,
            GroupName=nameTag['Value'],
            Description='allow http access to web server',
            VpcId=vpc.id,
            TagSpecifications = [ 
                {'ResourceType':'security-group', 
                "Tags": [flagTag, nameTag]
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
        stage = sgWeb.group_name+' created'
        logger.info(stage)        
    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2082)
        resp.err_resp()

    # 8-3: create database security group
    try:
        nameTag = {"Key": "Name", "Value": parm['securityGroup2']['tagName']}
        basePerm = check_perm(parm['securityGroup2'])
        sgDb = resource_ec2.create_security_group(
            DryRun=DryRun,
            GroupName=nameTag['Value'],
            Description='allow tcp access to database server',
            VpcId=vpc.id,
            TagSpecifications = [ 
                {'ResourceType':'security-group', 
                "Tags": [flagTag, nameTag]
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
        stage = sgWeb.group_name+' created'
        logger.info(stage)           
    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2083)
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

        stage = newDC.name+' metadata updated'
        logger.info(stage)

    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2092)
        resp.err_resp()

# step 10: Update Datacenter name list to DynamoDB
    try:
        # 待補充

        stage = newDC.name+' created successfully !'
        logger.info(stage)

        return newDC

    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2092)
        resp.err_resp()


# 根據勾選狀態匹配Security group IP規則
def check_perm(sg):
    sgpermList = []
    if sg["enableRDP"]:
        sgpermList.append({
            'IpProtocol': 'tcp',
            'FromPort': 3389,
            'ToPort': 3389,
#             'Ipv6Ranges': [], 
#             'PrefixListIds': [], 
#             'UserIdGroupPairs': [],            
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        })

    if sg["enableSSH"]:
        sgpermList.append({
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
#             'Ipv6Ranges': [], 
#             'PrefixListIds': [], 
#             'UserIdGroupPairs': [],            
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        })

    if sg["enablePing"]:
        sgpermList.append({
            'IpProtocol': 'icmp',
            'FromPort': 8,
            'ToPort': -1,
#             'Ipv6Ranges': [], 
#             'PrefixListIds': [], 
#             'UserIdGroupPairs': [],            
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        })
    return sgpermList
