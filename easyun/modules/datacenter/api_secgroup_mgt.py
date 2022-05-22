# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""
from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from .schemas import AddSecGroupParm, DelSecGroupParm, SecGroupDetail
from . import bp, get_secgroup, get_datacenter


@bp.post('/secgroup')
@auth_required(auth_token)
@bp.input(AddSecGroupParm)
def create_secgroup(parm):
    '''新建 SecurityGroup'''
    dcName = parm['dcName']
    tgName = parm['tgName']
    tgDesc = parm['tgDesc']
    tagName = parm['tagName']
    try:
        dc = get_datacenter(dcName)
        sg = dc.create_secgroup(tgName, tgDesc, tagName)
        sgList = sg.get_secgroup_list()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.get('/secgroup/<sg_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @bp.output(SecGroupDetail)
def get_secgroup_detail(sg_id, parm):
    '''查看 SecurityGroup 详细信息'''
    dcName = parm['dc']
    try:
        sg = get_secgroup(sg_id, dcName)
        sgDetail = sg.get_detail()
        resp = Result(detail=sgDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.delete('/secgroup')
@auth_required(auth_token)
@bp.input(DelSecGroupParm)
def delete_secgroup(parm):
    '''删除 SecurityGroup'''
    dcName = parm['dcName']
    sgId = parm['sgId']
    try:
        sg = get_secgroup(sgId, dcName)
        oprtRes = sg.delete()
        resp = Result(detail=oprtRes, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.put('/secgroup')
@auth_required(auth_token)
@bp.input(AddSecGroupParm)
def update_secgroup(parm):
    '''修改 SecurityGroup 【未完成】'''
    dcName = parm['dc']
    try:
        sg = get_secgroup(dcName)
        sgList = sg.get_secgroup_list()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()
