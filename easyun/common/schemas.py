# encoding: utf-8
"""
  @module:  Easyun Common Schema
  @desc:    Easyun通用Schema定义
  @auth:
"""

from apiflask import Schema
from apiflask.fields import Integer, String, DateTime
from apiflask.validators import Length, OneOf, Email
from easyun.cloud.aws.region import get_region_codes


class LoginParm(Schema):
    username = String(required=True, validate=Length(3, 20), metadata={"example": 'demo'})
    password = String(required=True, validate=Length(5, 30), metadata={"example": 'easyun'})


class UsernameParm(Schema):
    username = String(required=True, validate=Length(3, 20), metadata={"example": 'demo'})


class PasswordParm(Schema):
    password = String(required=True, validate=Length(5, 20), metadata={"example": "easyun"})


class AccountBasic(Schema):
    accountId = String()
    accountType = String()
    role = String()
    deployRegion = String()


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
    username = String(required=True, validate=Length(0, 20), metadata={"example": "user"})
    password = String(required=True, validate=Length(0, 30), metadata={"example": "PassW0rd"})
    email = String(required=True, validate=Email(), metadata={"example": "user@mail.com"})


class TagItem(Schema):
    Key = String(required=True, metadata={"example": 'Env'})
    Value = String(required=True, metadata={"example": 'Develop'})


class DcNameQuery(Schema):
    '''DataCenter name for query parm'''

    dc = String(
        required=True,
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()), metadata={"example": 'Easyun'},
    )


class RegionCodeQuery(Schema):
    '''Region code for query parm'''

    region = String(
        required=True, validate=OneOf(get_region_codes()), metadata={"example": 'us-east-1'}
    )


class RegionModel(Schema):
    regionCode = String(metadata={"example": 'us-east-1'})
    regionName = String(metadata={"example": 'US East (N. Virginia)'})
    countryCode = String(metadata={"example": 'USA'})


class DcNameParm(Schema):
    '''DataCenter name for body parm'''

    dcName = String(
        required=True,
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()), metadata={"example": 'Easyun'},
    )


class TaskIdQuery(Schema):
    id = String(
        required=True,  # task UUID
        validate=Length(0, 36), metadata={"example": "1603a978-e5a0-4e6a-b38c-4c751ff5fff8"},
    )


class TaskModel(Schema):
    taskId = String(metadata={"example": "1603a978-e5a0-4e6a-b38c-4c751ff5fff8"})
    # task.state: PENDING/STARTED/PROGRESS/SUCCESS/FAILURE
    status = String(metadata={"example": "STARTED"})
    description = String(metadata={"example": "Pubic subnet1 created."})
    current = Integer(metadata={"example": 25})
    total = Integer(metadata={"example": 100})


class MsgOut(Schema):
    msg = String(metadata={"example": "operation success"})


def get_dc_name():
    """
    获取当前请求的 datacenter 名称。
    优先 X-Datacenter header, 兼容 query ?dc= 和 body dcName
    """
    from flask import g, request
    return (
        g.get('dc_name')
        or request.args.get('dc')
        or (request.get_json(silent=True) or {}).get('dcName')
    )
