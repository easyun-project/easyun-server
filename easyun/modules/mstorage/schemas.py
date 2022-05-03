# encoding: utf-8
"""
  @module:  Storage Schemas
  @desc:    存储管理模块Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import String, Integer, List, Dict, Boolean, DateTime, Nested
from apiflask.validators import Length, OneOf
from easyun.common.schemas import TagItem


class BucketIdQuery(Schema):
    dc = String(required=True, example='Easyun')
    bkt = String(required=True, validate=Length(0, 30))


class ObjectKeyQuery(Schema):
    dc = String(required=True, example='Easyun')
    bkt = String(required=True, validate=Length(0, 30), example='my-bucket')
    key = String(required=True)


class BucketIdParm(Schema):
    dcName = String(required=True, example='Easyun')
    bucketId = String(required=True, validate=Length(0, 30), example='my-bucket')


class BucketCreateParm(Schema):
    regionCode = String(required=True, example='us-east-1')
    isEncryption = Boolean(required=True, example=False)
    isVersioning = Boolean(required=True, example=False)
    pubBlockConfig = Dict(
        example={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True,
        }
    )
    bucketACL = String(
        validate=OneOf(['private', 'public-read', 'public-read-write', 'authenticated-read']),
        example='private',
    )


class BucketPubBlockParm(Schema):
    bucketId = String(required=True, validate=Length(0, 60), example='new-bucket')
    newAcl = Boolean(required=True, example=True)
    allAcl = Boolean(required=True, example=True)
    newPolicy = Boolean(required=True, example=True)
    allPolicy = Boolean(required=True, example=True)


class AddBucketParm(Schema):
    dcName = String(required=True, example='Easyun')
    bucketId = String(required=True, validate=Length(0, 60), example='new-bucket')
    bucketCreateParm = Nested(BucketCreateParm)


class BucketBasic(Schema):
    bucketId = String(required=True, validate=Length(0, 60), example='my-bucket')
    createTime = DateTime(required=True, example="2022-02-20T09:59:21.61+00:00")
    bucketRegion = String(required=True, example='us-east-1')
    bucketUrl = String(example='my-bucket.s3.amazonaws.com')


class BucketAccess(Schema):
    status = String(example='private')
    description = String(example='All objects are private')


class BucketModel(Schema):
    bucketId = String(required=True, validate=Length(0, 60), example='my-bucket')
    createTime = DateTime(required=True, example="2022-02-20T09:59:21.61+00:00")
    bucketRegion = String(required=True, example='us-east-1')
    bucketUrl = String(example='my-bucket.s3.amazonaws.com')
    # bucketLifecycle = List(Dict())
    bucketAccess = Nested(
        BucketAccess,
        example={'status': 'private', 'description': 'All objects are private'}
    )
    bucketSize = Dict(
        example={'value': 123, 'unit': 'MiB'}
    )


class BucketPermission(Schema):
    status = String(example='private')
    description = String(example='All objects are private')
    bucketACL = String(example='private')
    pubBlockConfig = Dict(
        example={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True,
        }
    )
    

class BucketProperty(Schema):
    isEncryption = Boolean(required=True, example=False)
    isVersioning = Boolean(required=True, example=False)


class BucketDetail(Schema):
    bucketBasic = Nested(BucketBasic)
    bucketPermission = Nested(BucketPermission)
    bucketProperty = Nested(BucketProperty)
    userTags = Nested(TagItem(many=True))


class VolAttachment(Schema):
    svrId = String(required=True, example="i-09aa9e2c83d840ab1")
    tagName = String(example="test-devbk")
    attachPath = String(required=True, example="/dev/sdf")
    diskType = String(example="user")
    attachTime = DateTime(example="2022-02-27T02:20:44+00:00")


class VolumeConfig(Schema):
    volumeSize = Integer(example=10)
    volumeIops = Integer(example=3000)
    volumeThruput = Integer(example=500)
    isEncrypted = Boolean(example=False)


class VolumeBasic(Schema):
    volumeId = String(required=True, example="vol-0bd70f2001d6fb8bc")
    tagName = String(example="disk_test")
    isAttachable = Boolean(example=False)
    volumeState = String(example="in-use")
    volumeAz = String(example="us-east-1a")
    volumeType = String(example="gp3")
    volumeSize = Integer(example=10)
    createTime = DateTime(
        # 效果同 .isoformat()
        example="2022-02-20T09:59:21.61+00:00"
    )


class VolumeModel(Schema):
    volumeId = String(required=True, example="vol-0bd70f2001d6fb8bc")
    tagName = String(example="disk_test")
    volumeState = String(example="in-use")
    isAttachable = Boolean(example=False)
    volumeAz = String(example="us-east-1a")
    createTime = DateTime(
        # 效果同 .isoformat()
        example="2022-02-20T09:59:21.61+00:00"
    )
    volumeType = String(example="gp3")
    volumeSize = Integer(example=10)
    volumeIops = Integer(example=3000)
    volumeThruput = Integer(example=500)
    isEncrypted = Boolean(example=False)
    volumeAttach = Nested(VolAttachment(many=True))


class VolumeDetail(Schema):
    volumeBasic = Nested(VolumeBasic)
    volumeConfig = Nested(VolumeConfig)
    volumeAttach = Nested(VolAttachment(many=True))
    userTags = Nested(TagItem(many=True))


class AddVolumeParm(Schema):
    dcName = String(required=True, example="Easyun")
    volumeSize = Integer(required=True, example=10)
    volumeType = String(required=True, example='gp3')
    isEncrypted = Boolean(required=True, example=False)
    isMultiAttach = Boolean(example=False)
    volumeIops = Integer(example=3000)
    volumeThruput = Integer(example=500)
    azName = String(example='us-east-1a')
    tagName = String(example='disk_test')
    svrId = String(example='i-0ac436622e8766a13')  # 云服务器ID
    attachPath = String(example='/dev/sdf')


class DelVolumeParm(Schema):
    dcName = String(required=True, example="Easyun")
    volumeIds = List(
        String(),
        required=True,
        example=[
            'vol-05b06708c63dce7d9',
        ],
    )


class AttachVolParm(Schema):
    volumeId = String(required=True, example="vol-05b06708c63dce7d9")
    svrId = String(required=True, example='i-0ac436622e8766a13')  # 云服务器ID
    attachPath = String(example='/dev/sdf')


class DetachVolParm(Schema):
    volumeId = String(required=True, example="vol-05b06708c63dce7d9")
    svrId = String(required=True, example='i-0ac436622e8766a13')  # 云服务器ID
    attachPath = String(example='/dev/sdf')
