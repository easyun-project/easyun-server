# -*- coding: utf-8 -*-
"""
  @module:  Database Get Module
  @desc:    数据库相关信息GET API
  @auth:    aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.utils import len_iter, query_dc_region
from datetime import date, datetime
from . import bp


@bp.get('')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_database_detail():
    '''获取数据中心全部数据库(RDS)信息'''
    pass


@bp.get('/<rds_id>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def get_database_detail(rds_id):
    '''获取指定数据库(RDS)详细信息'''
    pass


@bp.get('/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SvrListOut, description='Get Servers list')
def list_database_brief(parm):
    '''获取数据中心全部数据库(RDS)列表[仅基础字段]'''
    pass
