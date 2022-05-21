# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""
from apiflask import input, output, auth_required
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.schemas import DcNameQuery
from .schemas import SecGroupBasic, SecGroupModel, DcParmIn
from . import bp, get_sec_group


@bp.get('/secgroup/{group_id}')
@auth_required(auth_token)
@bp.input(DcParmIn)
def get_secgroup_detail(parm):
    '''查看 SecurityGroup 详细信息'''
    dcName = parm['dc']
    try:
        sg = get_sec_group(dcName)
        sgList = sg.get_secgroup_list()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.delete('/secgroup')
@auth_required(auth_token)
@bp.input(DcParmIn)
def delete_secgroup(parm):
    '''删除 SecurityGroup'''
    dcName = parm['dc']
    try:
        sg = get_sec_group(dcName)
        sgList = sg.get_secgroup_list()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.post('/secgroup')
@auth_required(auth_token)
@bp.input(DcParmIn)
def create_secgroup(parm):
    '''新建 SecurityGroup'''
    dcName = parm['dc']
    try:
        sg = get_sec_group(dcName)
        sgList = sg.get_secgroup_list()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.put('/secgroup')
@auth_required(auth_token)
@bp.input(DcParmIn)
def update_secgroup(parm):
    '''修改 SecurityGroup'''
    dcName = parm['dc']
    try:
        sg = get_sec_group(dcName)
        sgList = sg.get_secgroup_list()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()
