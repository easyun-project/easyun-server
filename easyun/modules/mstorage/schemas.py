# encoding: utf-8
"""
  @module:  Storage Schemas
  @desc:    存储管理模块Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import String, Integer, List, Boolean, DateTime, Nested
from apiflask.validators import Length


class BktNameQuery(Schema):
    bktName = String(
        required=True, 
        validate=Length(0, 30)
    )
 
class ObjectListQuery(Schema):
    bktName = String(
        required=True
    )
    dcName = String(
        required=True,
        example='Easyun'
    )
class ObjectQuery(Schema):
    dcName = String(
        required=True,
        example='Easyun'
    )
    objectKey = String(
        required=True
    )
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



class AddVolumeParm(Schema):
    dcName = String(
        required=True,
        example="Easyun")
    volumeSize = Integer(
        required=True, 
        example=10)
    volumeType = String(
        required=True, 
        example='gp3')
    isEncrypted = Boolean(
        required=True, 
        example=False)
    volumeIops = Integer(
        example=3000)
    volumeThruput = Integer(
        example=500)
    azName = String(
        example='us-east-1a')
    tagName = String(
        example='disk_test')
    svrId = String(  # 云服务器ID
        example='i-0ac436622e8766a13')
    attachPath = String(
        example='/dev/sdf')


class DelVolumeParm(Schema):
    dcName = String(
        required=True,
        example="Easyun")
    volumeIds = List(
        String(),
        required=True,
        example=['vol-05b06708c63dce7d9',]    
    )    


class AttachVolParm(Schema):
    volumeId = String(
        required=True,
        example="vol-05b06708c63dce7d9")
    svrId = String(  # 云服务器ID
        required=True, 
        example='i-0ac436622e8766a13')
    attachPath = String(
        example='/dev/sdf')
        

class DetachVolParm(Schema):
    volumeId = String(
        required=True,
        example="vol-05b06708c63dce7d9")    
    svrId = String(  # 云服务器ID
        required=True, 
        example='i-0ac436622e8766a13')
    attachPath = String(
        example='/dev/sdf')


class VolAttachment(Schema):
    attachSvrId = String(
        required=True, 
        example= "i-09aa9e2c83d840ab1")
    attachSvr = String(
        example= "test-devbk")        
    attachPath = String(
        required=True,
        example= "/dev/sdf")
    diskType = String(
        example= "user")
    attachTime = DateTime(
        example= "2022-02-27T02:20:44+00:00")


class VolumeDetail(Schema):
    volumeId = String(
        required=True,         
        example= "vol-0bd70f2001d6fb8bc")
    tagName = String(
        example= "disk_test")
    volumeState = String(
        example= "in-use")
    isEncrypted = Boolean(
        example=False)        
    volumeAz = String(
        example= "us-east-1a")
    createTime = DateTime(
        # 效果同 .isoformat()
        example= "2022-02-20T09:59:21.61+00:00")
    volumeType = String(
        example="gp3")
    volumeIops = Integer(
        example=3000)
    volumeSize = Integer(
        example=10)
    volumeThruput = Integer(
        example=500)
    volumeAttach = Nested(VolAttachment(many=True))



class newVolume(Schema):
    az = String(required=True)
    instanceId = String(required=True)
    diskType = String(required=True)
    size = String(required=True)
    iops = String(required=True)
    thruput = String(required=True)
    diskPath = String(required=True)
    encryption = String(required=True)


