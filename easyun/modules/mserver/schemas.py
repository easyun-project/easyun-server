# encoding: utf-8
"""
  @module:  Server Schema
  @desc:    Server Input/output schema
  @author:  aleck
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested
from apiflask.validators import Length, OneOf


class SvrIdParm(Schema):
    svrId =  String(        #云服务器ID
        required=True,
        example=["i-0e7105687e0fec039",]
    )


class ModSvrNameParm(Schema):
    svrIds = List(         #云服务器IDs
        String(),
        required=True,
        example=['i-0e5250487e0fec039','i-0dfc0232b2f4f8ab9']
    )
    svrName = String(         #云服务器新Name
        required=True,
        example='new_server_name'
    )


class SvrIdList(Schema):
    svrIds = List(         #云服务器ID
        String(),
        required=True,
        example=['i-0e5250487e0fec039','i-0dfc0232b2f4f8ab9']
    )


# 定义api返回格式 Schema，以Out结尾
class SvrOperateOut(Schema):
    svrId = List(String)
    currState = List(String) 
    preState = List(String) 


class TagItem(Schema):
    Key= String(
        required=True,
        example='Env'
    )
    Value= String(
        required=True,
        example='Develop'
    )


class SvrTagNameItem(Schema):
    svrId =  String(
        example=["i-0e7105687e0fec039",]
    )
    tagName = String(
        example='server_name'
    )
