# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Get Module
  @desc:    数据中心相关信息GET API
  @auth:    aleck
"""

from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result
from easyun.common.schemas import get_dc_name, RegionModel, MsgOut
from easyun.cloud import get_cloud, get_datacenter, get_account
from .schemas import DataCenterBasic, DataCenterModel, RouteTableModel
from . import bp


@bp.get('')
@bp.auth_required(auth_token)
@bp.output(DataCenterModel(many=True), description='List all DataCenter')
def list_datacenter_detail():
    '''获取Easyun管理的所有数据中心信息'''
    try:
        thisAccount: Account = Account.query.first()
        cloud = get_cloud(thisAccount.account_id, thisAccount.aws_type)

        allDcList = cloud.list_all_datacenter()
        resp = Result(detail=allDcList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2001)
        response.err_resp()


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.output(DataCenterBasic(many=True), description='Get DataCenter List')
def list_datacenter_brief():
    '''获取Easyun管理的数据中心列表[仅基础字段]'''
    try:
        thisAccount: Account = Account.query.first()
        cloud = get_cloud(thisAccount.account_id, thisAccount.aws_type)

        dcList = cloud.get_datacenter_list()
        resp = Result(detail=dcList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2002)
        response.err_resp()


@bp.get('/region')
@bp.auth_required(auth_token)
@bp.output(RegionModel(many=True), description='Get Region List')
def list_aws_region():
    '''获取可用的Region列表'''
    try:
        account = get_account()
        regionList = [
            {'regionCode': r['regionCode'], 'regionName': r['regionName'].get('eng'), 'countryCode': r['countryCode']}
            for r in account.list_regions()
        ]
        resp = Result(detail=regionList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2005)
        response.err_resp()


@bp.get('/region/zones')
@bp.auth_required(auth_token)
@bp.output(MsgOut)
def get_available_zones():
    '''获取可用的Region列表'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        azoneList = dc.get_azone_list()

        resp = Result(detail=azoneList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2006)
        response.err_resp()


@bp.get('/routetable')
@bp.auth_required(auth_token)
@bp.output(RouteTableModel(many=True))
def list_all_route():
    '''获取 全部路由表(route table)信息'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        rtbList = dc.list_all_routetable()
        resp = Result(detail=rtbList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2601)
        resp.err_resp()
