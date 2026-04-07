# -*- coding: utf-8 -*-
"""
  @module:  Database Get Module
  @desc:    数据库相关信息GET API
"""

from easyun.common.auth import auth_token
from easyun.common.schemas import DcNameQuery, get_dc_name
from easyun.common.result import Result
from easyun.providers import get_datacenter
from .schemas import DbiDetailItem, DbiBriefItem
from . import bp


@bp.get('')
@bp.auth_required(auth_token)
@bp.output(DbiDetailItem(many=True))
def list_database_detail():
    '''获取数据中心全部数据库(RDS)信息'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        dbiList = dc.resource.list_all_dbinstance()

        resp = Result(detail=dbiList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=5001)
        return resp.err_resp()


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.output(DbiBriefItem(many=True))
# @bp.output(SvrListOut, description='Get Servers list')
def list_database_brief():
    '''获取数据中心全部数据库(RDS)列表[仅基础字段]'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        dbiList = dc.resource.get_dbinstance_list()

        resp = Result(detail=dbiList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=5002)
        return resp.err_resp()


@bp.get('/<rds_id>')
@bp.auth_required(auth_token)
@bp.output(DbiDetailItem)
def get_database_detail(rds_id):
    '''获取指定数据库(RDS)详细信息'''
    dcName = get_dc_name()
    # 设置 boto3 接口默认 region_name
    # dcRegion = set_boto3_region(dcName)
    try:
        dc = get_datacenter(dcName)
        dbi = dc.get_db_instance(rds_id)
        dbiDetail = dbi.get_detail()

        response = Result(detail=dbiDetail, status_code=200)
        return response.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=5003)
        response.err_resp()
