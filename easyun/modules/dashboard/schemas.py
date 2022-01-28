#!/usr/bin/env python
# encoding: utf-8
"""
  @module:  Dashboard Schema
  @desc:    Dashboard Input/output schema
  @author:  aleck
"""
from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from marshmallow.fields import Nested

class DcNameQuery(Schema):
    dc = String(
        required=True, 
        validate=Length(0, 30),
        example='Easyun'
    )