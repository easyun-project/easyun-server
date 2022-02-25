# -*- coding: utf-8 -*-
"""
  @module:  DataCenter: Gateway
  @desc:    Datacenter gateway management, including Internet Gateway and NAT Gateway
  @auth:    aleck
"""

import boto3
from datetime import datetime
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.utils import len_iter, query_dc_region
from . import bp


@bp.get('/igw')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_igw_detail(param):
    '''获取全部Internet网关(IGW)信息'''
    pass


@bp.get('/natgw')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_natgw_detail(param):
    '''获取全部NAT网关(NAT GW)信息'''
    pass
