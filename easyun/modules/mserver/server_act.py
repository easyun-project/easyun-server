# -*- coding: utf-8 -*-
"""
  @module:
  @desc: Server Management - action: start, restart, stop, delete
"""
from apiflask import Schema
from apiflask.fields import String, List
from apiflask.validators import OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.providers import get_datacenter
from .schemas import SvrIdList, SvrOperateOut, SvrStateChangeItem
from . import bp


class OperateIn(Schema):
    svr_ids = List(String(), required=True)
    action = String(required=True, validate=OneOf(['start', 'stop', 'restart']))
    dcName = String(required=True, metadata={"example": "Easyun"})


@bp.post('/action')
@bp.auth_required(auth_token)
@bp.input(OperateIn, arg_name='operate')
@bp.output(SvrStateChangeItem(many=True))
def operate_svr(operate):
    '''启动/停止/重启 云服务器'''
    try:
        dc = get_datacenter(operate['dcName'])
        results = []
        for svr_id in operate['svr_ids']:
            svr = dc.get_server(svr_id)
            if operate['action'] == 'start':
                svr.start()
                results.append({'svrId': svr_id, 'currState': 'pending', 'preState': 'stopped'})
            elif operate['action'] == 'stop':
                svr.stop()
                results.append({'svrId': svr_id, 'currState': 'stopping', 'preState': 'running'})
            elif operate['action'] == 'restart':
                svr.reboot()
                results.append({'svrId': svr_id, 'currState': 'rebooting', 'preState': 'running'})
        resp = Result(detail=results, status_code=200)
        return resp.make_resp()
    except Exception as e:
        resp = Result(message=str(e), status_code=3004, http_status_code=400)
        resp.err_resp()


@bp.delete('')
@bp.auth_required(auth_token)
@bp.input(SvrIdList, arg_name='parm')
@bp.output(SvrStateChangeItem(many=True))
def delete_svr(parm):
    '''删除(Terminate)云服务器'''
    try:
        dc = get_datacenter(parm['dcName'])
        deleteList = []
        for svr_id in parm['svrIds']:
            svr = dc.get_server(svr_id)
            svr.delete()
            deleteList.append({'svrId': svr_id, 'currState': 'shutting-down', 'preState': 'running'})
        resp = Result(detail=deleteList, status_code=200)
        return resp.make_resp()
    except Exception:
        resp = Result(message='Delete server failed', status_code=3004, http_status_code=400)
        return resp.err_resp()
