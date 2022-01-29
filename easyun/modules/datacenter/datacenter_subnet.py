# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from flask import request
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.result import Result
from easyun.common.utils import len_iter, query_region
from . import bp, DryRun
from .schemas import DataCenterEIPIn,DataCenterListsIn,DataCenterListIn,DcParmIn,DcNameQuery,DataCenterSubnetIn,DataCenterSubnetInsert


@bp.get('/subnet')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# # @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_subnet_detail(param):
    '''获取数据中心全部subnet信息'''
    # only for globa regions
    # dc_name=request.args.get("dc_name")
    # type=request.args.get("subnet")

    dcName=param.get('dc')
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
        # if thisDC == None:
        #     response = Result(detail ={'Result' : 'Errors'}, message='No Datacenter available, kindly create it first!', status_code=3001,http_status_code=400)
        #     response.err_resp() 
        client_ec2 = boto3.client('ec2', region_name= thisDC.region)

        subnets = client_ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Flag', 'Values': [dcName]
                },             
            ]
        )
        subnetList = []
        for subnet in subnets['Subnets']:
            subnet_record = {
                'tagName': [tag.get('Value') for tag in subnet['Tags'] if tag.get('Key') == 'Name'][0],
                'subnetType':'public',  # public/private
                'subnetState':subnet['State'],
                'subnetId':subnet['SubnetId'],
                'subnetVpc':subnet['VpcId'],
                'subnetAz':subnet['AvailabilityZone'],
                'cidrBlock4':subnet['CidrBlock'],
                'ipv4Count':subnet['AvailableIpAddressCount'],
                'mapPubip':subnet['MapPublicIpOnLaunch']
            }
            subnetList.append(subnet_record)
    
        resp = Result(
            detail = subnetList,
            status_code=200
        )
        return resp.make_resp()
    except Exception as e:
        resp = Result(
            detail=str(e), 
            status_code=2030
        )
        resp.err_resp()


@bp.get('/subnet/<subnet_id>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# # @output(SubnetsOut, description='List DataCenter Subnets Resources')
def get_subnet_detail(subnet_id, param):
    '''获取指定subnet的信息'''

    dcName = param.get('dc')
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
        resource_ec2 = boto3.resource('ec2', region_name= thisDC.region)
        thisSubnet =  resource_ec2.Subnet(subnet_id)
        # 统计subnet下的服务器数量
        svrCollection = thisSubnet.instances.all()
        svrNum = len_iter(svrCollection)
        # 统计subnet下的网卡数量
        eniCollection = thisSubnet.network_interfaces.all()
        eniNum = len_iter(svrCollection)
        # 判断subnet type是 public 还是 private
        '''待实现'''
        subnetType = 'public'

        subnetAttributes = {
            'tagName': [tag.get('Value') for tag in thisSubnet.tags if tag.get('Key') == 'Name'][0],
            'subnetType':subnetType,
            'subnetState':thisSubnet.state,
            'subnetId':thisSubnet.subnet_id,
            'subnetVpc':thisSubnet.vpc_id,
            'subnetAz':thisSubnet.availability_zone,
            'cidrBlock4':thisSubnet.cidr_block,
            'ipv4Count':thisSubnet.available_ip_address_count,
            'mapPubip':thisSubnet.map_public_ip_on_launch,
            'svrNum':svrNum,
            'eniNum':eniNum
        }

        resp = Result(
            detail = subnetAttributes,
            status_code=200
        )
        return resp.make_resp()

    except Exception as e:
        resp = Result(
            detail=str(e), 
            status_code=2031
        )
        return resp.err_resp()


@bp.get('/subnet/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# # @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_subnet_brief(param):
    '''获取数据中心subnet列表[仅基础字段]'''
    subnetList = [
        {
            'tagName':'Public subnet 1',
            'subnetType':'public',
            'subnetId':'subnet-0dd77078e6ddba304',
            'subnetAz':'us-east-1a',
            'cidrBlock4':'10.11.1.0/24'
        },
        {
            'tagName':'Public subnet 2',
            'subnetType':'public',
            'subnetId':'subnet-096bb246c63812505',
            'subnetAz':'us-east-1c',
            'cidrBlock4':'10.11.2.0/24'
        },        
        {
            'tagName':'Private subnet 1',
            'subnetType':'private',
            'subnetId':'subnet-0c03d878665e84b13',
            'subnetAz':'us-east-1a',
            'cidrBlock4':'10.11.21.0/24'
        },
        {
            'tagName':'Private subnet 2',
            'subnetType':'private',
            'subnetId':'subnet-00d617ca17c12edb5',
            'subnetAz':'us-east-1c',
            'cidrBlock4':'10.11.22.0/24'
        }
    ]

    resp = Result(
        detail = subnetList,
        status_code=200
    )
    return resp.make_resp()    


@bp.delete('/subnet')
# @auth_required(auth_token)
@input(DataCenterSubnetIn)
def delete_subnet(param):
    '''删除数据中心subnet mock'''
    dcName=param.get('dcName')
    subnetID=param.get('subnetID')

    dcTag = {"Key": "Flag", "Value": dcName}
  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    if (thisDC is None):
            response = Result(message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
            response.err_resp() 
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    try:
        response = client_ec2.delete_subnet(SubnetId=subnetID,DryRun=DryRun)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = Result(
                detail = [],
                status_code = 200 
            )
            return resp.make_resp()
        else:
            resp = Result(detail=[], status_code=2061)
            resp.err_resp()
    except Exception as ex:
        resp = Result(message='delete subnet failed due to invalid subnetID' ,status_code=2061,http_status_code=400)
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()

    resp = Result(
        detail = "subnet id got deleted!",
        status_code = 200 
    )
    return resp.make_resp()


@bp.post('/subnet')
#@auth_required(auth_token)
@input(DataCenterSubnetInsert)
# @output(DcResultOut, 201, description='add A new Datacenter')
def add_subnet(param):
    '''添加数据中心subnet mock'''
    dcName=param.get('dcName')
    subnetCIDR=param.get('subnetCDIR')

    dcTag = {"Key": "Flag", "Value": dcName}
  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    if (thisDC is None):
            response = Result(message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
            response.err_resp() 
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    nameTag = {"Key": "Name", "Value": "VPC-"+dcName}
       
    try:
        subnetID = client_ec2.create_subnet(
            CidrBlock=subnetCIDR, 
            VpcId=thisDC.vpc_id,
            TagSpecifications= [
                {
                    'ResourceType':'subnet', 
                    "Tags": [dcTag, nameTag]
                }
            ],
            DryRun=DryRun)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = Result(
                detail = [{'subnetID': subnetID['Subnet']['SubnetId']}],
                status_code = 200 
            )
            return resp.make_resp()
        else:
            resp = Result(detail=[], status_code=2061)
            resp.err_resp()
    except Exception as ex:
        resp = Result(message='create subnet failed due to invalid subnetID' ,status_code=2061,http_status_code=400)
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()

    resp = Result(
        detail = {"subnetId", 'subnet-123123'},
        status_code = 200 
    )
    return resp.make_resp()


@bp.put('/subnet')
#@auth_required(auth_token)
# @input(DataCenterSubnetInsert)
# @output(DcResultOut, 201, description='add A new Datacenter')
def mod_subnet(param):
    '''修改数据中心subnet [mock]'''

    resp = Result(
        detail = {"subnetId", 'subnet-123456'},
        status_code = 200 
    )
    return resp.make_resp()