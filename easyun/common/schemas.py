# encoding: utf-8
"""
  @module:  Easyun Common Schema
  @desc:    Easyun通用Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested
from apiflask.validators import Length, OneOf
from easyun.cloud.utils import query_dc_list
from easyun.cloud.aws_region import get_region_codes


class DcNameQuery(Schema):
    ''' datacenter name for query parm '''
    dc = String(
        required=True, 
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()),
        example='Easyun'
    )


class RegionCodeQuery(Schema):
    ''' datacenter name for query parm '''
    region = String(
        required=True, 
        validate=OneOf(get_region_codes()),
        example='us-east-1'
    )



class DcNameParm(Schema):
    ''' datacenter name for body parm '''
    dcName = String(
        required=True, 
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()),
        example='Easyun'
    )
    