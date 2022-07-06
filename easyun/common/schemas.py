# encoding: utf-8
"""
  @module:  Easyun Common Schema
  @desc:    Easyun通用Schema定义
  @auth:
"""

from apiflask import Schema
from apiflask.fields import Integer, String, DateTime, Number
from apiflask.validators import Length, OneOf, Email
from easyun.cloud.aws_region import get_region_codes


class LoginParm(Schema):
    username = String(required=True, validate=Length(3, 20), example='demo')
    password = String(required=True, validate=Length(5, 30), example='Passw0rd')


class UsernameParm(Schema):
    username = String(required=True, validate=Length(3, 20), example='demo')


class PasswordParm(Schema):
    password = String(required=True, validate=Length(5, 20), example="Passw0rd")


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
    username = String(required=True, validate=Length(0, 20), example="user")
    password = String(required=True, validate=Length(0, 30), example="PassW0rd")
    email = String(required=True, validate=Email(), example="user@mail.com")


class TagItem(Schema):
    Key = String(required=True, example='Env')
    Value = String(required=True, example='Develop')


class DcNameQuery(Schema):
    '''DataCenter name for query parm'''

    dc = String(
        required=True,
        validate=Length(0, 30),
        # validate=OneOf(query_dc_list()),
        example='Easyun',
    )


class RegionCodeQuery(Schema):
    '''Region code for query parm'''

    region = String(
        required=True, validate=OneOf(get_region_codes()), example='us-east-1'
    )


class RegionModel(Schema):
    regionCode = String(example='us-east-1')
    regionName = String(example='US East (N. Virginia)')
    countryCode = String(example='USA')


class DcNameParm(Schema):
    '''DataCenter name for body parm'''

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


class TaskModel(Schema):
    taskId = String(example="1603a978-e5a0-4e6a-b38c-4c751ff5fff8")
    # task.state: PENDING/STARTED/PROGRESS/SUCCESS/FAILURE
    status = String(example="STARTED")
    description = String(example="Pubic subnet1 created.")
    current = Number(example=25)
    total = Number(example=100)
