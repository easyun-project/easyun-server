# encoding: utf-8
"""
  @module:  Server Schema
  @desc:    Server Input/output schema
  @author:  aleck
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested
from apiflask.validators import Length, OneOf



class SvrIdList(Schema):
    svrIds = List(         #云服务器ID
        String(),
        required=True,
        example=["i-0710xxxxxxxxxxxxx",]
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
