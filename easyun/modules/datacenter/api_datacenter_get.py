# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Get Module
  @desc:    数据中心相关信息GET API
  @auth:    aleck
"""

from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery, RegionModel
from easyun.cloud import get_aws_cloud
from easyun.cloud.aws import get_datacenter
from .schemas import DataCenterBasic, DataCenterModel
from . import bp


@bp.get('')
@auth_required(auth_token)
@bp.output(DataCenterModel(many=True), description='List all DataCenter')
def list_datacenter_detail():
    '''获取Easyun管理的所有数据中心信息'''
    try:
        thisAccount: Account = Account.query.first()
        cloud = get_aws_cloud(thisAccount.account_id, thisAccount.aws_type)

        allDcList = cloud.list_all_datacenter()
        resp = Result(detail=allDcList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2001)
        response.err_resp()


@bp.get('/list')
@auth_required(auth_token)
@bp.output(DataCenterBasic(many=True), description='Get DataCenter List')
def list_datacenter_brief():
    '''获取Easyun管理的数据中心列表[仅基础字段]'''
    try:
        thisAccount: Account = Account.query.first()
        cloud = get_aws_cloud(thisAccount.account_id, thisAccount.aws_type)

        dcList = cloud.get_datacenter_list()
        resp = Result(detail=dcList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2002)
        response.err_resp()


@bp.get('/region')
@auth_required(auth_token)
@bp.output(RegionModel(many=True), description='Get Region List')
def list_aws_region():
    '''获取可用的Region列表'''
    try:
        thisAccount: Account = Account.query.first()
        cloud = get_aws_cloud(thisAccount.account_id, thisAccount.aws_type)

        regionList = cloud.get_region_list('ec2')

        resp = Result(detail=regionList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2005)
        response.err_resp()


@bp.get('/region/zones')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def get_available_zones(parm):
    '''获取可用的Region列表'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        azoneList = dc.get_azone_list()

        resp = Result(detail=azoneList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2006)
        response.err_resp()


@bp.get('/routetable')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_all_route(param):
    '''获取 全部路由表(route table)信息'''
    dcName = param['dc']
    try:
        dc = get_datacenter(dcName)
        rtbList = dc.list_all_routetable()
        resp = Result(detail=rtbList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2601)
        resp.err_resp()
