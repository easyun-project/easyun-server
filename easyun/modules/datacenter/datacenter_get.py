# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Get Module
  @desc:    数据中心相关信息GET API
  @auth:      
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.utils import len_iter, query_dc_region, gen_dc_tag
from datetime import date, datetime
from .schemas import ResourceListOut, DataCenterListOut, DCInfoOut, VpcListOut,DataCenterListIn
from . import bp



@bp.get('')
@auth_required(auth_token)
# @output(DataCenterListOut, description='Get DataCenter List')
def list_datacenter_detail():
    '''获取Easyun管理的所有数据中心信息'''
    try:
        thisAccount:Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id = thisAccount.account_id)
        dcList = []
        for dc in dcs:
            resource_ec2 = boto3.resource('ec2', region_name= dc.region)
            vpc = resource_ec2.Vpc(dc.vpc_id)
            dcItem = {
                'dcName' : dc.name,
                'dcRegion' : dc.region,
                'vpcID' : dc.vpc_id,
                'vpcCidr' : vpc.cidr_block,
                'dcUser' : dc.create_user,
                'createDate' : dc.create_date.isoformat(),
                'createUser' : dc.create_user,
                'dcAccount' : dc.account_id,                
            }
            dcList.append(dcItem)
        
        resp = Result(
            detail = dcList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=2001,
            http_status_code=400)
        response.err_resp()


@bp.get('/<dc_name>')
@auth_required(auth_token)
# @app_log('')
# @output(DCInfoOut, description='Get Datacenter Metadata')
def get_datacenter_detail(dc_name):
    '''获取指定的数据中心信息'''
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dc_name).first()
        dcRegion = thisDC.get_region()

        resource_ec2 = boto3.resource('ec2', region_name= dcRegion)
        dcVPC = resource_ec2.Vpc(thisDC.vpc_id)
        dcItem = {
            'dcName' : thisDC.name,
            'dcRegion' : thisDC.region,
            'vpcID' : thisDC.vpc_id,
            'vpcCidr' : dcVPC.cidr_block,
            'createDate' : thisDC.create_date.isoformat(),
            'createUser' : thisDC.create_user,
            'dcAccount' : thisDC.account_id,
        }
        
        resp = Result(
            detail = dcItem,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=2012,http_status_code=400
        )
        response.err_resp()


@bp.get('/list')
@auth_required(auth_token)
# @output(DataCenterListOut, description='Get DataCenter List')
def list_datacenter_brief():
    '''获取Easyun管理的数据中心列表[仅基础字段]'''
    try:
        thisAccount:Account = Account.query.first()
        dcs = Datacenter.query.filter_by(account_id = thisAccount.account_id)
        dcList = []
        for dc in dcs:
            dcItem = {
                'dcName' : dc.name,
                'dcRegion' : dc.region,
                'vpcID' : dc.vpc_id
            }
            dcList.append(dcItem)
        
        resp = Result(
            detail = dcList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, 
            status_code=2001,
            http_status_code=400)
        response.err_resp()


@bp.get('/<service>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(ResourceListOut, description='Get DataCenter Resources')
def list_dc_service(service, parm):
    '''获取当前数据中心基础服务信息[Mock]'''
    # 数据中心基础服务区别于计算、存储、数据库等资源；
    # 数据中心基础服务包含： vpc、subnet、securitygroup、gateway、route、eip 等
    #
    # 先写在一个查询api里，建议拆分到每个服务模块里
    if service not in ['all','vpc','azone','subnet','secgroup','gateway','route','eip']:
        resp = Result(
            detail='Unknown input resource.',
            message='Validation error',
            status_code=2020,
            http_status_code=400
        )
        return resp.err_resp()

    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = parm['dc']).first()
        dcRegion = thisDC.get_region()
        # 设置 boto3 接口默认 region_name
        # boto3.setup_default_session(region_name = dcRegion )

        client_ec2 = boto3.client('ec2', region_name = dcRegion)
        resource_ec2 = boto3.resource('ec2', region_name = dcRegion)
        # vpcs = client_ec2.describe_vpcs(Filters=[{'Name': 'tag:Flag','Values': parm['dc']}])

        if service == 'vpc':
            '''获取数据中心 VPC 信息'''
            vpcId = thisDC.vpc_id            
            dcVPC = resource_ec2.Vpc(vpcId)
            vpcAttributes = {
                'tagName': [tag.get('Value') for tag in dcVPC.tags if tag.get('Key') == 'Name'][0],
                'vpcId':dcVPC.vpc_id,
                'cidrBlock':dcVPC.cidr_block,
                'vpcState':dcVPC.state,
                'vpcDefault':dcVPC.is_default
            }
            resp = Result(
                detail = vpcAttributes,
                status_code=200
            )

        if service == 'azone':
            '''获取数据中心 Availability Zone 信息'''
            # only for globa regions
            azs = client_ec2.describe_availability_zones()
            azList = [az['ZoneName'] for az in azs['AvailabilityZones']]            
            resp = Result(
                detail = azList,
                status_code=200
            )

        return resp.make_resp()
        
    except Exception as ex:
        resp = Result(
            detail=str(ex), 
            status_code=2030
        )
        return resp.err_resp()
