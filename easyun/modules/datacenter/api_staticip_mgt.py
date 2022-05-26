# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

from apiflask import APIBlueprint
from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery, DcNameParm
from easyun.cloud.aws import get_staticip, get_datacenter
from .schemas import DelEipParm, StaticIPBasic, StaticIPModel


bp = APIBlueprint('StaticIP', __name__, url_prefix='/staticip')


@bp.get('')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(StaticIPModel(many=True), description='List all StaticIP')
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


@bp.get('/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(StaticIPBasic(many=True), description='Get StaticIP brief List')
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


@bp.post('')
@auth_required(auth_token)
@bp.input(DcNameParm)
# @output(DcResultOut, 201, description='add A new Datacenter')
def add_eip(parm):
    '''新增 静态IP(EIP)'''
    dcName = parm['dcName']
    tagName = parm.get('tagName')
    try:
        dc = get_datacenter(dcName)
        newEip = dc.create_staticip(tagName)
        resp = Result(
            detail=newEip,
            status_code=200,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2061, http_status_code=400)
        resp.err_resp()


@bp.get('/<eip_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def get_eip_detail(eip_id, parm):
    '''获取 指定静态IP(EIP)信息'''
    dcName = parm['dc']
    try:
        eip = get_staticip(eip_id, dcName)
        eipDetail = eip.get_detail()
        resp = Result(
            detail=eipDetail,
            status_code=200,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2101)
        resp.err_resp()


@bp.delete('')
@auth_required(auth_token)
@bp.input(DelEipParm)
def delete_eip(parm):
    '''删除 指定静态IP(EIP)'''
    dcName = parm['dcName']
    eipId = parm['eipId']
    try:
        eip = get_staticip(eipId, dcName)
        oprtRes = eip.delete()
        resp = Result(
            detail=oprtRes,
            status_code=200,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2061)
        resp.err_resp()
