# -*- coding: utf-8 -*-
"""
  @file:    datacenter_delete.py
  @desc:    DataCenter Deletion module
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
from .datacenter_sdk import datacentersdk

# from . import vpc_act
from .schemas import VpcListOut

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
                {"Key": "Flag", "Value": FLAG},
                {"Key": "Name", "Value": 'test-from-api'}
            ]
        }
        ]
}

@bp.get('/dc_info/<vpc_id>')
#@auth_required(auth_token)
#@input(VpcListIn)
# @app_log('')
@output(VpcListOut, description='Get Datacenter info')
def get_vpc(vpc_id):
    '''获取当前Datacenter资源信息'''
    # get vpc info
    # get subnet info
    # get securitygroup info
    # get keypair info

    ec2 = boto3.client('ec2', region_name=REGION)
    vpcs = ec2.describe_vpcs( VpcIds=[
        vpc_id,
    ],
    Filters=[
        {'Name': 'tag:Flag','Values': [FLAG]}
    ])
    vpclist = {}
    print(json.dumps(vpcs, sort_keys=True, indent=4))

    response = Result(detail = vpcs, status_code=3001)
    return response.make_resp()

#    return jsonify(vpcs)
    


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