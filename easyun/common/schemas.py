# encoding: utf-8
"""
  @module:  Easyun Common Schema
  @desc:    Easyun通用Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested
from apiflask.validators import Length, OneOf


class DcNameQuery(Schema):
    dc = String(
        required=True, 
        validate=Length(0, 30),
        example='Easyun'
    )