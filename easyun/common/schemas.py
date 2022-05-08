# encoding: utf-8
"""
  @module:  Easyun Common Schema
  @desc:    Easyun通用Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import Integer, String, DateTime, Field, Nested
from apiflask.validators import Length, OneOf, Email
from easyun.cloud.aws_region import get_region_codes


class LoginParm(Schema):
    username = String(required=True, validate=Length(0, 20), example='demo')
    password = String(required=True, validate=Length(0, 30), example='Passw0rd')


class UsernameParm(Schema):
    username = String(required=True, validate=Length(0, 20), example='demo')


class PasswordParm(Schema):
    passWord = String(required=True, validate=Length(0, 20), example="Passw0rd")


class UserModel(Schema):
    id = Integer()
    username = String()
    email = String()
    token = String()
    tokenExpiration = DateTime()
    # cloud account info
    accountId = String()
    accountType = String()
    role = String()
    deployRegion = String()


class UserBasic(Schema):
    id = Integer()
    username = String()
    email = String()


class AddUserParm(Schema):
    username = String(required=True, validate=Length(0, 20), example="user")
    password = String(required=True, validate=Length(0, 30), example="passWord")
    email = String(required=True, validate=Email(), example="user@mail.com")


class TagItem(Schema):
    Key = String(required=True, example='Env')
    Value = String(required=True, example='Develop')


class DcNameQuery(Schema):
    '''datacenter name for query parm'''

    dc = String(
        required=True,
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()),
        example='Easyun',
    )


class RegionCodeQuery(Schema):
    '''datacenter name for query parm'''

    region = String(
        required=True, validate=OneOf(get_region_codes()), example='us-east-1'
    )


class DcNameParm(Schema):
    '''datacenter name for body parm'''

    dcName = String(
        required=True,
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()),
        example='Easyun',
    )


class TaskIdQuery(Schema):
    id = String(
        required=True,  # celery task UUID
        validate=Length(0, 36),
        example="1603a978-e5a0-4e6a-b38c-4c751ff5fff8",
    )
