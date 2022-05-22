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
from easyun.common.schemas import DcNameQuery
from easyun.cloud.aws import AWSCloud
from .schemas import DataCenterBasic, DataCenterModel, RegionModel, SecGroupBasic, SecGroupModel, SubnetBasic, SubnetModel
from . import bp, get_datacenter


_AWS_CLOUD = None


def get_aws_cloud(account_id, account_type):
    global _AWS_CLOUD
    if _AWS_CLOUD is not None and _AWS_CLOUD.account_id == account_id:
        return _AWS_CLOUD
    else:
        return AWSCloud(account_id, account_type)


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


@bp.get('/zones')
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


@bp.get('/subnet')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(SubnetModel(many=True), description='List DataCenter Subnets Resources')
def list_subnet_detail(parm):
    '''获取 全部subnet子网信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        subnetList = dc.list_all_subnet()

        resp = Result(detail=subnetList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(detail=str(ex), status_code=2101)
        resp.err_resp()


@bp.get('/subnet/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(SubnetBasic(many=True), description='List DataCenter Subnets Resources')
def list_subnet_brief(parm):
    '''获取 全部subnet子网列表[仅基础字段]'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        subnetList = dc.get_subnet_list()

        resp = Result(detail=subnetList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(detail=str(ex), status_code=2102)
        resp.err_resp()


@bp.get('/secgroup')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(SecGroupModel(many=True), description='List all SecurityGroups Resources')
def list_secgroup_detail(parm):
    '''获取数据中心全部SecurityGroup信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        sgList = dc.list_all_secgroup()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2201)
        resp.err_resp()


@bp.get('/secgroup/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(SecGroupBasic(many=True), description='Get SecurityGroup brief list')
def list_secgroup_brief(parm):
    '''获取 全部SecurityGroup列表[仅基础字段]'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        sgList = dc.get_secgroup_list()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2202)
        resp.err_resp()


@bp.get('/staticip')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_eip_detail(param):
    '''获取 全部静态IP(EIP)信息'''
    dcName = param['dc']
    try:
        dc = get_datacenter(dcName)
        eipList = dc.list_all_staticip()
        resp = Result(detail=eipList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2301)
        resp.err_resp()


@bp.get('/staticip/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def list_eip_brief(param):
    '''获取 全部静态IP列表(EIP)[仅基础字段]'''
    dcName = param['dc']
    try:
        dc = get_datacenter(dcName)
        eipList = dc.list_all_staticip()
        resp = Result(detail=eipList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2302)
        resp.err_resp()


@bp.get('/gateway/internet')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_all_igw(param):
    '''获取全部Internet网关(igw)信息'''
    dcName = param['dc']
    try:
        dc = get_datacenter(dcName)
        eipList = dc.list_all_intgateway()
        resp = Result(detail=eipList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2401)
        resp.err_resp()


@bp.get('/gateway/nat')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_all_natgw(param):
    '''获取全部NAT网关(natgw)信息'''
    dcName = param['dc']
    try:
        dc = get_datacenter(dcName)
        eipList = dc.list_all_natgateway()
        resp = Result(detail=eipList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2501)
        resp.err_resp()


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
