# -*- coding: utf-8 -*-
"""
  @module:  DataCenter: Gateway
  @desc:    Datacenter gateway management, including Internet Gateway and NAT Gateway
  @auth:    aleck
"""

from apiflask import APIBlueprint
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from .schemas import AddIntGateway, AddNatGateway
from easyun.cloud.aws import get_datacenter, get_int_gateway, get_nat_gateway


bp = APIBlueprint('Gateway', __name__, url_prefix='/gateway')


@bp.get('/internet')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='param')
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


@bp.post('/internet')
@bp.auth_required(auth_token)
@bp.input(AddIntGateway, arg_name='parm')
def create_intgateway(parm):
    '''新建 Internet Gateway'''
    dcName = parm['dcName']
    tagName = parm['tagName']
    try:
        dc = get_datacenter(dcName)
        newIgw = dc.create_int_gateway(tagName)
        resp = Result(detail=dict(newIgw), status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.get('/nat')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='param')
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


@bp.post('/nat')
@bp.auth_required(auth_token)
@bp.input(AddNatGateway, arg_name='parm')
def create_natgateway(parm):
    '''新建 NAT Gateway'''
    dcName = parm['dcName']
    connectType = parm['connectType']
    subnetId = parm['subnetId']
    allocationId = parm['allocationId']
    tagName = parm['tagName']
    try:
        dc = get_datacenter(dcName)
        netNat = dc.create_nat_gateway(connectType, subnetId, allocationId, tagName)
        resp = Result(detail=dict(netNat), status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.get('/internet/<igw_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
def get_igw_detail(igw_id, parm):
    '''查看 Internet Gateway 详细信息'''
    dcName = parm['dc']
    try:
        igw = get_int_gateway(igw_id, dcName)
        igwDetail = igw.get_detail()
        resp = Result(detail=igwDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.get('/nat/<natgw_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
def get_natgw_detail(natgw_id, parm):
    '''查看 Internet Gateway 详细信息'''
    dcName = parm['dc']
    try:
        natgw = get_nat_gateway(natgw_id, dcName)
        natDetail = natgw.get_detail()
        resp = Result(detail=natDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()
