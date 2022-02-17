# -*- coding: utf-8 -*-
"""
  @module:  Storage Bucket Detail
  @desc:    Get bucket detail info
  @auth:    
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.schemas import DcNameQuery
from . import bp



@bp.get('/bucket/<bkt_id>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def get_bkt_detail(bkt_id, parm):
    '''获取指定存储桶(Bucket)详细信息'''
    dcName=parm.get('dc')
    pass