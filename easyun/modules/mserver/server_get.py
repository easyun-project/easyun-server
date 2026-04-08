# -*- coding: utf-8 -*-
'''
  @module:  Server Management 
  @desc: Get info: Server list, Server detail
'''
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import get_dc_name
from easyun.cloud import get_datacenter
from . import bp
from .schemas import SvrDetailItem, SvrBriefItem


@bp.get('')
@bp.auth_required(auth_token)
@bp.output(SvrDetailItem(many=True))
def list_server_detail():
    '''获取数据中心全部云服务器信息'''
    try:
        dc = get_datacenter(get_dc_name())
        resp = Result(detail=dc.resource.list_all_server(), status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=3001, http_status_code=400)
        return resp.err_resp()


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.output(SvrBriefItem(many=True))
def list_server_brief():
    '''获取数据中心全部云服务器列表[仅基础字段]'''
    try:
        dc = get_datacenter(get_dc_name())
        resp = Result(detail=dc.resource.list_server_brief(), status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=3001, http_status_code=400)
        return resp.err_resp()
