# -*- coding: utf-8 -*-
"""
  @module:  DataCenter: Gateway
  @desc:    Datacenter gateway management, including Internet Gateway and NAT Gateway
  @auth:    aleck
"""

from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from .schemas import AddIntGateway, AddNatGateway
from easyun.cloud.aws import InternetGateway, NatGateway
from . import bp, get_datacenter


_INTERNET_GATEWAY = None
_NAT_GATEWAY = None


def get_int_gw(igw_id, dc_name):
    global _INTERNET_GATEWAY
    if _INTERNET_GATEWAY is not None and _INTERNET_GATEWAY.igwId == igw_id:
        return _INTERNET_GATEWAY
    else:
        return InternetGateway(igw_id, dc_name)


def get_nat_gw(igw_id, dc_name):
    global _NAT_GATEWAY
    if _NAT_GATEWAY is not None and _NAT_GATEWAY.igwId == igw_id:
        return _NAT_GATEWAY
    else:
        return NatGateway(igw_id, dc_name)


@bp.post('/gateway/internet')
@auth_required(auth_token)
@bp.input(AddIntGateway)
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


@bp.post('/gateway/nat')
@auth_required(auth_token)
@bp.input(AddNatGateway)
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


@bp.get('/gateway/internet/<igw_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def get_igw_detail(igw_id, parm):
    '''查看 Internet Gateway 详细信息'''
    dcName = parm['dc']
    try:
        igw = get_int_gw(igw_id, dcName)
        igwDetail = igw.get_detail()
        resp = Result(detail=igwDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.get('/gateway/nat/<natgw_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def get_natgw_detail(natgw_id, parm):
    '''查看 Internet Gateway 详细信息'''
    dcName = parm['dc']
    try:
        natgw = get_nat_gw(natgw_id, dcName)
        natDetail = natgw.get_detail()
        resp = Result(detail=natDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()
