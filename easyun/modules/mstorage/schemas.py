# encoding: utf-8
"""
  @module:  Storage Schemas
  @desc:    存储管理模块Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import String, Integer, List, Boolean, DateTime, Nested
from apiflask.validators import Length


class TagItem(Schema):
    Key= String(
        required=True,
        example='Env'
    )
    Value= String(
        required=True,
        example='Develop'
    )

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



class VolAttachment(Schema):
    svrId = String(
        required=True, 
        example= "i-09aa9e2c83d840ab1")
    tagName = String(
        example= "test-devbk")        
    attachPath = String(
        required=True,
        example= "/dev/sdf")
    diskType = String(
        example= "user")
    attachTime = DateTime(
        example= "2022-02-27T02:20:44+00:00")

class volumeConfig(Schema):
    volumeSize = Integer(
        example=10)        
    volumeIops = Integer(
        example=3000)
    volumeThruput = Integer(
        example=500)
    isEncrypted = Boolean(
        example=False)

class VolumeModel(Schema):
    volumeId = String(
        required=True,         
        example= "vol-0bd70f2001d6fb8bc")
    tagName = String(
        example= "disk_test")
    volumeState = String(
        example= "in-use")
    isAttachable = Boolean(
        example=False)   
    volumeAz = String(
        example= "us-east-1a")
    createTime = DateTime(
        # 效果同 .isoformat()
        example= "2022-02-20T09:59:21.61+00:00")
    volumeType = String(
        example="gp3")
    volumeSize = Integer(
        example=10)        
    volumeIops = Integer(
        example=3000)
    volumeThruput = Integer(
        example=500)
    isEncrypted = Boolean(
        example=False)        
    volumeAttach = Nested(VolAttachment(many=True))

class VolumeBasic(Schema):
    volumeId = String(
        required=True,         
        example= "vol-0bd70f2001d6fb8bc")
    tagName = String(
        example= "disk_test")
    isAttachable = Boolean(
        example=False)
    volumeState = String(
        example= "in-use")
    volumeAz = String(
        example= "us-east-1a")
    volumeType = String(
        example="gp3")
    volumeSize = Integer(
        example=10)
    createTime = DateTime(
        # 效果同 .isoformat()
        example= "2022-02-20T09:59:21.61+00:00")    

class VolumeDetail(Schema):
    volumeBasic = Nested(VolumeBasic)
    volumeConfig = Nested(volumeConfig)
    volumeAttach = Nested(VolAttachment(many=True))
    userTags = Nested(TagItem(many=True))



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
    isMultiAttach = Boolean(
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


