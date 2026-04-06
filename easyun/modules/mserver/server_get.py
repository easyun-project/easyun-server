# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get info: Server list, Server detail
'''
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.providers import get_datacenter
from . import bp
from .schemas import SvrDetailItem, SvrBriefItem


@bp.get('')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(SvrDetailItem(many=True))
def list_server_detail(parm):
    '''获取数据中心全部云服务器信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        svrList = dc.resource.list_all_server()
        resp = Result(detail=svrList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=3001, http_status_code=400)
        return resp.err_resp()


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(SvrBriefItem(many=True))
def list_server_brief(parm):
    '''获取数据中心全部云服务器列表[仅基础字段]'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        svrList = dc.resource.list_server_brief()
        resp = Result(detail=svrList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=3001, http_status_code=400)
        return resp.err_resp()
