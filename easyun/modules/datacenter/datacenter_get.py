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
from flask import session
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.cloud.aws_region import query_country_code, query_region_name
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
            message= str(ex), 
            status_code=2001,
            http_status_code=400)
        response.err_resp()


@bp.get('/region')
@auth_required(auth_token)
def list_aws_region():
    '''获取可用的Region列表'''
    try:
        thisAccount:Account = Account.query.first()
        boto3Session = boto3._get_default_session()
        if thisAccount.aws_type == 'GCR':
            regionList = boto3Session.get_available_regions('ec2', 'aws-cn')
        else:
            # aws_type == Global
            regionList = boto3Session.get_available_regions('ec2')

        resp = Result(
            detail = [
                {
                    'regionCode': r,
                    'regionName': query_region_name(r),
                    'countryCode': query_country_code(r)
                } for r in regionList
            ],
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        response = Result(
            message= str(ex), 
            status_code=2005,
            http_status_code=400)
        response.err_resp()
