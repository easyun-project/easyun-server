# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Get Module
  @desc:    数据中心相关信息GET API
  @auth:    aleck
"""

import boto3
from botocore.exceptions import ClientError
from apiflask import auth_required
from sqlalchemy import true
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.result import Result
from easyun.cloud.aws_region import query_country_code, query_region_name
from .schemas import DefaultParmQuery, DefaultParmsOut, DataCenterBasic, DataCenterModel
from . import bp


@bp.get('')
@auth_required(auth_token)
@bp.output(DataCenterModel(many=true), description='List all DataCenter')
def list_datacenter_detail():
    '''获取Easyun管理的所有数据中心信息'''
    try:
        thisAccount: Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id=thisAccount.account_id)
        dcList = []
        for dc in dcs:
            resource_ec2 = boto3.resource('ec2', region_name=dc.region)
            # error handing for InvalidVpcID.NotFound
            try:
                vpc = resource_ec2.Vpc(dc.vpc_id)
                dcItem = {
                    'dcName': dc.name,
                    'regionCode': dc.region,
                    'vpcID': dc.vpc_id,
                    'cidrBlock': vpc.cidr_block,
                    'createDate': dc.create_date,
                    'createUser': dc.create_user,
                    'accountId': dc.account_id,
                }
                dcList.append(dcItem)
            except ClientError:
                continue
        resp = Result(detail=dcList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2001, http_status_code=400)
        response.err_resp()


@bp.get('/list')
@auth_required(auth_token)
@bp.output(DataCenterBasic(many=true), description='Get DataCenter List')
def list_datacenter_brief():
    '''获取Easyun管理的数据中心列表[仅基础字段]'''
    try:
        thisAccount: Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id=thisAccount.account_id)
        dcList = []
        for dc in dcs:
            dcItem = {'dcName': dc.name, 'regionCode': dc.region, 'vpcID': dc.vpc_id}
            dcList.append(dcItem)

        resp = Result(detail=dcList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2001, http_status_code=400)
        response.err_resp()


@bp.get('/region')
@auth_required(auth_token)
def list_aws_region():
    '''获取可用的Region列表'''
    try:
        thisAccount: Account = Account.query.first()
        boto3Session = boto3._get_default_session()
        if thisAccount.aws_type == 'GCR':
            regionList = boto3Session.get_available_regions('ec2', 'aws-cn')
        else:
            # aws_type == Global
            regionList = boto3Session.get_available_regions('ec2')

        resp = Result(
            detail=[
                {
                    'regionCode': r,
                    'regionName': query_region_name(r),
                    'countryCode': query_country_code(r),
                }
                for r in regionList
            ],
            status_code=200,
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2005, http_status_code=400)
        response.err_resp()


@bp.get('/default')
@auth_required(auth_token)
@bp.input(DefaultParmQuery, location='query')
@bp.output(DefaultParmsOut, description='Get DataCenter Parameters')
def get_default_parms(parm):
    '''获取创建云数据中心默认参数'''
    inputName = parm['dc']
    inputRegion = parm.get('region')
    try:
        # Check if the DC Name is available
        thisDC: Datacenter = Datacenter.query.filter_by(name=inputName).first()
        if thisDC is not None:
            raise ValueError('DataCenter name already existed')

        # tag:Name prefix for all resource, eg. easyun-xxx
        prefix = inputName.lower()

        # get account info from database
        curr_account: Account = Account.query.first()
        # set deploy_region as default region
        if inputRegion is None:
            inputRegion = curr_account.get_region()

        # get az list
        client_ec2 = boto3.client('ec2', region_name=inputRegion)
        azs = client_ec2.describe_availability_zones()
        azList = [az['ZoneName'] for az in azs['AvailabilityZones']]

        # define default vpc parameters
        defaultVPC = {
            'cidrBlock': '10.10.0.0/16',
            # 'vpcCidrv6' : '',
            # 'vpcTenancy' : 'Default',
        }

        # define default igw
        defaultIgw = {
            # 这里为igw的 tag:Name，创建首个igw的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'igw')
        }

        # define default natgw
        defaultNatgw = {
            # 这里为natgw的 tag:Name ，创建首个natgw的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'natgw')
        }

        gwList = [defaultIgw["tagName"], defaultNatgw["tagName"]]

        # define default igw route table
        defaultIrtb = {
            # 这里为igw routetable 的 tag:Name, 创建首个igw routetable 的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'rtb-igw')
        }

        # define default natgw route table
        defaultNrtb = {
            # 这里为nat routetable 的 tag:Name ，创建首个nat routetable 的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'rtb-natgw')
        }

        rtbList = [defaultIrtb["tagName"], defaultNrtb["tagName"]]

        dcParms = {
            # default selected parameters
            "dcName": inputName,
            "dcRegion": inputRegion,
            'dcVPC': defaultVPC,
            "pubSubnet1": {
                "tagName": "Public subnet 1",
                "cidrBlock": "10.10.1.0/24",
                "azName": azList[0],
                "gwName": defaultIgw["tagName"],
                "routeTable": defaultIrtb["tagName"],
            },
            "pubSubnet2": {
                "tagName": "Public subnet 2",
                "cidrBlock": "10.10.2.0/24",
                "azName": azList[1],
                "gwName": defaultIgw["tagName"],
                "routeTable": defaultIrtb["tagName"],
            },
            "priSubnet1": {
                "tagName": "Private subnet 1",
                "cidrBlock": "10.10.21.0/24",
                "azName": azList[0],
                "gwName": defaultNatgw["tagName"],
                "routeTable": defaultNrtb["tagName"],
            },
            "priSubnet2": {
                "tagName": "Private subnet 2",
                "cidrBlock": "10.10.22.0/24",
                "azName": azList[1],
                "gwName": defaultNatgw["tagName"],
                "routeTable": defaultNrtb["tagName"],
            },
            "securityGroup0": {
                "tagName": '%s-%s' % (prefix, 'sg-default'),
                # 该标记对应是否增加 In-bound: Ping 的安全组规则
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False,
            },
            "securityGroup1": {
                "tagName": '%s-%s' % (prefix, 'sg-webapp'),
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False,
            },
            "securityGroup2": {
                "tagName": '%s-%s' % (prefix, 'sg-database'),
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False,
            },
        }
        dropDown = {
            # for DropDownList
            "azList": azList,
            "gwList": gwList,
            "rtbList": rtbList,
        }

        response = Result(
            detail={'dcParms': dcParms, 'dropDown': dropDown}, status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2001, http_status_code=400)
        resp.err_resp()
