# -*- coding: utf-8 -*-
"""
  @module:
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

from apiflask import APIBlueprint
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.providers import get_datacenter
from .schemas import DcMsgOut, AddSecGroupParm, DelSecGroupParm, SecGroupDetail, SecGroupBasic, SecGroupModel


bp = APIBlueprint('SecurityGroup', __name__, url_prefix='/secgroup')


@bp.get('')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
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


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
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


@bp.post('')
@bp.auth_required(auth_token)
@bp.input(AddSecGroupParm, arg_name='parm')
@bp.output(SecGroupModel)
def create_secgroup(parm):
    '''新建 SecurityGroup'''
    dcName = parm['dcName']
    tgName = parm['tgName']
    tgDesc = parm['tgDesc']
    tagName = parm['tagName']
    try:
        dc = get_datacenter(dcName)
        newSg = dc.create_secgroup(tgName, tgDesc, tagName)
        resp = Result(detail=newSg, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.get('/<sg_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
# @bp.output(SecGroupDetail)
@bp.output(SecGroupDetail)
def get_secgroup_detail(sg_id, parm):
    '''查看 SecurityGroup 详细信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        sg = dc.get_secgroup(sg_id)
        sgDetail = sg.get_detail()
        resp = Result(detail=sgDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.delete('')
@bp.auth_required(auth_token)
@bp.input(DelSecGroupParm, arg_name='parm')
@bp.output(DcMsgOut)
def delete_secgroup(parm):
    '''删除 SecurityGroup'''
    dcName = parm['dcName']
    sgId = parm['sgId']
    try:
        dc = get_datacenter(dcName)
        sg = dc.get_secgroup(sgId)
        oprtRes = sg.delete()
        resp = Result(detail=oprtRes, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.put('')
@bp.auth_required(auth_token)
@bp.input(AddSecGroupParm, arg_name='parm')
@bp.output(SecGroupModel)
def update_secgroup(parm):
    '''修改 SecurityGroup 【未完成】'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        sgList = dc.list_all_secgroup()
        resp = Result(detail=sgList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()
