# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Creation
  @desc:    create some datacenter basic service, like vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

from email import message
import boto3
from datetime import date, datetime
from apiflask import Schema, input, output, doc, abort, auth_required
from apiflask.fields import Integer, String, List, Dict, DateTime, Boolean
from apiflask.validators import Length, OneOf
from easyun import db, log
from easyun.cloud.aws_quota import get_quota_value
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.utils import len_iter, gen_dc_tag
from easyun.common.result import Result, make_resp, error_resp, bad_request
from .schemas import CreateDcParms, CreateDcResult
from . import bp, logger, DryRun


@bp.post('')
@auth_required(auth_token)
@input(CreateDcParms)
@output(CreateDcResult)
@log.api_error(logger)
def create_datacenter(parm):
    '''创建 Datacenter 及基础资源'''
    
    # Datacenter basic attribute define
    dcName = parm['dcName']
    dcRgeion = parm['dcRegion']
    # Mandatory tag:Flag for all resource
    flagTag = gen_dc_tag(dcName)
    
    boto3.setup_default_session(region_name = dcRgeion ) 
    resource_ec2 = boto3.resource('ec2')
    client_ec2 = boto3.client('ec2')

    # Step 0: Check the prerequisites for creating new datacenter
    try:
        # Check if the DC Name is available
        thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
        if (thisDC is not None):
            raise ValueError('DataCenter name already existed')
        # Check if VPC quota is enough
        vpcQuota = get_quota_value('vpc','L-F678F1CE')
        vpcIter = resource_ec2.vpcs.all()
        if len_iter(vpcIter)  >= int(vpcQuota):
            raise ValueError('The VPCs per Region limit has been reached')
        # Check if EIP quota is enough
        eipQuota = get_quota_value('ec2','L-0263D0A3')
        eipIter = resource_ec2.vpc_addresses.all()
        if len_iter(eipIter) >= int(eipQuota):
            raise ValueError('The EC2-VPC Elastic IPs limit has been reached')
 
    except Exception as ex:
        resp = Result(
            message=str(ex), 
            status_code=2001,
            http_status_code=400)
        resp.err_resp()

    # Step 1: create easyun vpc, including:
    # 1* main route table
    # 1* default security group
    # 1* default Network ACLs
    try:
        nameTag = {"Key": "Name", "Value": "VPC-"+dcName}
        vpc = resource_ec2.create_vpc(
            CidrBlock= parm['dcVPC']['cidrBlock'],
            TagSpecifications = [
                {
                    'ResourceType':'vpc', 
                    "Tags": [flagTag, nameTag]
                }
            ]
        )
        stage = vpc.id+' created'
        logger.info('[VPC]'+stage)
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2010)
        resp.err_resp()


   # step 2: Write VPC metadata to local database
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

        stage = '[DataCenter]'+newDC.name+' metadata updated'
        logger.info(stage)

    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2092)
        resp.err_resp()


    # step 3: create Internet Gateway
    try:
        nameTag = {"Key": "Name", "Value": parm['pubSubnet1']['gwName']}
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
        logger.info('[IGW]'+stage)

        # and Attach the igw to vpc
        igw.attach_to_vpc(
            DryRun = DryRun,
            VpcId = vpc.id
        )
        stage = igw.id+" attached to "+vpc.id
        logger.info('[IGW]'+stage)

    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2020)
        resp.err_resp()


    # step 4: create 2x Public Subnets
    try:
        nameTag = {"Key": "Name", "Value": parm['pubSubnet1']['tagName']}
        pubsbn1 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['pubSubnet1']['cidrBlock'],
            AvailabilityZone = parm['pubSubnet1']['azName'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = pubsbn1.id+' created'
        logger.info('[Subnet]'+stage)
        
        nameTag = {"Key": "Name", "Value": parm['pubSubnet2']['tagName']}
        pubsbn2 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['pubSubnet2']['cidrBlock'],
            AvailabilityZone = parm['pubSubnet2']['azName'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = pubsbn2.id+' created'
        logger.info('[Subnet]'+stage)
        
    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2030)
        resp.err_resp()


    # step 5: update main route table （route-igw）
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
                logger.info('[RouteTable]'+stage)
                
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
        resp = Result(message=str(ex) , status_code=2040)
        resp.err_resp()


    # step 6: create 2x Private Subnets
    try:
        nameTag = {"Key": "Name", "Value": parm['priSubnet1']['tagName']}
        prisbn1 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['priSubnet1']['cidrBlock'],
            AvailabilityZone = parm['priSubnet1']['azName'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = prisbn1.id+' created'
        logger.info('[Subnet]'+stage)
        
        nameTag = {"Key": "Name", "Value": parm['priSubnet2']['tagName']}
        prisbn2 = resource_ec2.create_subnet(
            DryRun=DryRun,
            CidrBlock= parm['priSubnet2']['cidrBlock'],
            AvailabilityZone = parm['priSubnet2']['azName'],
            VpcId = vpc.id,
            TagSpecifications = [
                {
                    'ResourceType':'subnet', 
                    'Tags': [flagTag, nameTag]
                }
            ]
        )
        stage = prisbn2.id+' created'
        logger.info('[Subnet]'+stage)
        
    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2050)
        resp.err_resp()


    # step 7: create NAT Gateway with EIP
    # 7-1: Allocate EIP for NAT Gateway
    try:
        nameTag = {"Key": "Name", "Value": dcName.lower()+"-natgw-eip"}
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
        logger.info('[EIP]'+stage)
  
    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2061)
        resp.err_resp()

    # 7-2: create nat gateway
    try:
        nameTag = {"Key": "Name", "Value": parm['priSubnet1']['gwName']}
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
        logger.info('[NatGW]'+stage)

        # waite natgw created
        try:    
            waiter = client_ec2.get_waiter('nat_gateway_available')
            waiter.wait(NatGatewayIds=[natgwID])            
            stage = natgwID+' created'
            logger.info('[NatGW]'+stage)
        except Exception as ex:
            resp = Result(message=str(ex) , status_code=2062)
            resp.err_resp()

    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2060)
        resp.err_resp()


    # step 8: create NAT route table and route to natgw
    # 8-1 create route table for natgw
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
        logger.info('[Route]'+stage)

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
        resp = Result(message=str(ex) , status_code=2070)
        resp.err_resp()


    # step 9: update and create Security Groups
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

    # 9-1: update default security group
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
        stage = '[SecGroup]'+sg.group_name+' updated'
        logger.info(stage)

    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2081)
        resp.err_resp()

    # 9-2: create webapp security group
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
        stage = '[SecGroup]'+sgWeb.group_name+' created'
        logger.info(stage)        
    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2082)
        resp.err_resp()

    # 9-3: create database security group
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
        stage = '[SecGroup]'+sgWeb.group_name+' created'
        logger.info(stage)           
    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2083)
        resp.err_resp()


# step 10: Update Datacenter name list to DynamoDB
    try:
        # 待補充

        stage = '[DataCenter]'+newDC.name+' created successfully !'
        logger.info(stage)

        resp = Result(
            detail = newDC, 
            status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex) , status_code=2092)
        resp.err_resp()


def check_perm(sg):
    '''根據勾選狀態匹配SecGroup IP規則'''
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
