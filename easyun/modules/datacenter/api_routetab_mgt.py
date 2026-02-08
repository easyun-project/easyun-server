# -*- coding: utf-8 -*-
"""
  @desc:    Route table management module API
  @LastEditors: aleck
"""

from apiflask import APIBlueprint
from easyun.common.auth import auth_token
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.cloud.aws import get_datacenter, get_routetable
from .schemas import AddRouteTableParm, DelRouteTableParm, RouteTableBasic, RouteTableModel, RouteTableDetail


bp = APIBlueprint('Route', __name__, url_prefix='/routetable')


@bp.get('')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(RouteTableModel(many=True), description='List DataCenter RouteTables Resources')
def list_routetable_detail(parm):
    '''获取 全部RouteTable路由表信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        rtbList = dc.list_all_routetable()
        resp = Result(detail=rtbList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(detail=str(ex), status_code=2101)
        resp.err_resp()


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(RouteTableBasic(many=True), description='List DataCenter RouteTables Resources')
def list_routetable_brief(parm):
    '''获取 全部RouteTable路由表[仅基础字段]'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        rtbList = dc.list_all_routetable()
        resp = Result(detail=rtbList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(detail=str(ex), status_code=2102)
        resp.err_resp()


@bp.get('/<rtb_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
# @bp.output(RouteTableDetail, description='List DataCenter RouteTables Resources')
def get_routetable_detail(rtb_id, parm):
    '''获取 指定RouteTable路由表详细信息【to-be-done】'''
    dcName = parm['dc']
    try:
        rtb = get_routetable(rtb_id, dcName)
        rtbDetail = rtb.get_detail()
        resp = Result(detail=rtbDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.delete('')
@bp.auth_required(auth_token)
@bp.input(DelRouteTableParm, arg_name='parms')
def delete_routetable(parms):
    '''删除 指定RouteTable路由表【to-be-done】'''
    dcName = parms['dcName']
    rtbId = parms['rtbId']
    try:
        rtb = get_routetable(rtbId, dcName)
        oprtRes = rtb.delete()
        resp = Result(detail=oprtRes, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2061)
        resp.err_resp()


@bp.post('')
@bp.auth_required(auth_token)
@bp.input(AddRouteTableParm, arg_name='parms')
# @bp.output(DcResultOut, 201, description='add A new Datacenter')
def add_routetable(parms):
    '''新增 RouteTable路由表【to-be-done】'''
    dcName = parms['dcName']

    try:
        newRouteTable = 'developing'
        resp = Result(detail=newRouteTable, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2011)
        resp.err_resp()
