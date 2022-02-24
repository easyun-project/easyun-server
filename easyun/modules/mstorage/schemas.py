# encoding: utf-8
"""
  @module:  Storage Schemas
  @desc:    存储管理模块Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length


class BktNameQuery(Schema):
    bktName = String(
        required=True, 
        validate=Length(0, 30)
    )
class ObjectListQuery(Schema):
    bktName = String(
        required=True, 
        validate=Length(0, 30)
    )
    dcName = String(
        required=True,
        example='Easyun'
    )
    
class newVolume(Schema):
    az = String(required=True)
    instanceId = String(required=True)
    diskType = String(required=True)
    size = String(required=True)
    iops = String(required=True)
    thruput = String(required=True)
    diskPath = String(required=True)
    encryption = String(required=True)


class newBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )
    versioningConfiguration = String(required=True)
    bucketEncryption = String(required=True)
    region = String(required=True)

class deleteBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )

class vaildateBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )