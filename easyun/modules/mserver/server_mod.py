# -*- coding: utf-8 -*-
'''
@Description: Server Management - Modify: Name, Instance type, Protection
'''
from apiflask import Schema
from apiflask.fields import String, List
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import get_dc_name
from easyun.cloud import get_datacenter
from .schemas import ModSvrNameParm, SvrTagNameItem, ModSvrProtectionParm, SvrProtectionOut, MsgOut
from . import bp


@bp.get('/name/<svr_id>')
@bp.auth_required(auth_token)
@bp.output(SvrTagNameItem)
def get_svr_name(svr_id):
    '''查询指定云服务器的名称'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(svr_id)
        response = Result(detail={'svrId': svr_id, 'tagName': svr.tagName}, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3101, http_status_code=400)
        response.err_resp()


@bp.put('/name')
@bp.auth_required(auth_token)
@bp.input(ModSvrNameParm, arg_name='parms')
@bp.output(SvrTagNameItem(many=True))
def update_svr_name(parms):
    '''修改指定云服务器名称'''
    try:
        dc = get_datacenter(get_dc_name())
        results = []
        for svr_id in parms.get('svrIds', []):
            svr = dc.get_server(svr_id)
            svr.set_name(parms['svrName'])
            results.append({'svrId': svr_id, 'tagName': svr.tagName})
        response = Result(detail=results, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3102, http_status_code=400)
        response.err_resp()


@bp.put('/protection')
@bp.auth_required(auth_token)
@bp.input(ModSvrProtectionParm, arg_name='parms')
@bp.output(SvrProtectionOut)
def update_svr_protection(parms):
    '''修改指定云服务器protection'''
    try:
        dc = get_datacenter(get_dc_name())
        value = parms['action'] == 'disable'
        successIds = []
        for svr_id in parms.get('svrIds', []):
            svr = dc.get_server(svr_id)
            if svr.svrObj.state['Name'] == 'stopped':
                svr.set_protection(value)
                successIds.append(svr_id)
        failedIds = list(set(parms['svrIds']) - set(successIds))
        response = Result(detail={'success': successIds, 'failed': failedIds}, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3102, http_status_code=400)
        response.err_resp()


class ConfigIn(Schema):
    svrIds = List(String(), required=True, metadata={"example": ['i-01b565d505d5e0559']})
    insType = String(required=True, metadata={"example": 't3.small'})


@bp.post('/config')
@bp.auth_required(auth_token)
@bp.input(ConfigIn, arg_name='new')
@bp.output(MsgOut)
def update_config(new):
    '''修改指定云服务器实例配置'''
    try:
        dc = get_datacenter(get_dc_name())
        for svr_id in new['svrIds']:
            svr = dc.get_server(svr_id)
            svr.set_instance_type(new['insType'])
        response = Result(detail={'msg': 'config success'}, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3001, http_status_code=400)
        response.err_resp()
