# encoding: utf-8
"""
  @module:  Easyun Common Schema
  @desc:    Easyun通用Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested
from apiflask.validators import Length, OneOf
from .utils import query_dc_list


class DcNameQuery(Schema):
    ''' datacenter name for query parm '''
    dc = String(
        required=True, 
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()),
        example='Easyun'
    )


class DcNameBody(Schema):
    ''' datacenter name for body parm '''
    dcName = String(
        required=True, 
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()),
        example='Easyun'
    )
    