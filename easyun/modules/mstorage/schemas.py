# encoding: utf-8
"""
  @module:  Storage Schemas
  @desc:    存储管理模块Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import String, Integer, List, Dict, Boolean, DateTime, Nested
from apiflask.validators import Length, OneOf, Regexp
from easyun.common.schemas import TagItem


class BucketIdQuery(Schema):
    dc = String(required=True, metadata={"example": 'Easyun'})
    bkt = String(required=True, validate=Length(0, 30), metadata={"example": 'bktexample17'})


class BucketIdParm(Schema):
    dcName = String(required=True, metadata={"example": 'Easyun'})
    bucketId = String(required=True, validate=Length(0, 30), metadata={"example": 'my-bucket'})


class BucketOptions(Schema):
    regionCode = String(required=True, metadata={"example": 'us-east-1'})
    isEncryption = Boolean(required=True, metadata={"example": False})
    isVersioning = Boolean(required=True, metadata={"example": False})
    pubBlockConfig = Dict(metadata={"example": {
            'isBlockNewAcls': True,
            'isBlockAllAcls': True,
            'isBlockNewPolicy': True,
            'isBlockAllPolicy': True,
        }}
    )
    bucketACL = String(
        validate=OneOf(
            ['private', 'public-read', 'public-read-write', 'authenticated-read']
        ), metadata={"example": 'private'},
    )


S3_REPORT_NAME_PATTERN = "[0-9A-Za-z!\\-_.*\'()]+"
S3_PREFIX_PATTERN = "[0-9A-Za-z!\\-_.*\\'()/]*"
BUCKET_NANE_PATTERN = "(?!^(\d{1,3}\.){3}\d{1,3}$)(^[a-z0-9]([a-z0-9-]*(\.[a-z0-9])?)*$)"
VOLUME_TYPES = ['gp2', 'gp3', 'io1', 'io2', 'sc1', 'st1', 'standard']

class AddBucketParm(Schema):
    dcName = String(required=True, metadata={"example": 'Easyun'})
    bucketId = String(
        required=True,
        validate=[Regexp(BUCKET_NANE_PATTERN, error='only lowercase letters, numbers, dots(.) and hyphens(-)'), Length(3, 63)], metadata={"example": 'my-bucket'}
    )
    bucketOptions = Nested(BucketOptions)


class BucketPropertyParm(Schema):
    # dcName = String(example='Easyun')
    # bucketId = String(required=True, validate=Length(3, 63), metadata={"example": 'my-bucket'})
    isEncryption = Boolean(metadata={"example": True})
    isVersioning = Boolean(metadata={"example": True})


class BucketPublicParm(Schema):
    # bucketId = String(required=True, validate=Length(0, 60), metadata={"example": 'my-bucket'})
    isBlockNewAcls = Boolean(required=True, metadata={"example": True})
    isBlockAllAcls = Boolean(required=True, metadata={"example": True})
    isBlockNewPolicy = Boolean(required=True, metadata={"example": True})
    isBlockAllPolicy = Boolean(required=True, metadata={"example": True})


class BucketBasic(Schema):
    bucketId = String(required=True, validate=Length(0, 60), metadata={"example": 'my-bucket'})
    createTime = DateTime(required=True, metadata={"example": '2022-02-20T09:59:21.61+00:00'})
    bucketRegion = String(required=True, metadata={"example": 'us-east-1'})
    bucketUrl = String(metadata={"example": 'my-bucket.s3.amazonaws.com'})


class BucketAccess(Schema):
    status = String(metadata={"example": 'private'})
    description = String(metadata={"example": 'All objects are private'})


class BucketModel(Schema):
    bucketId = String(required=True, validate=Length(0, 60), metadata={"example": 'my-bucket'})
    createTime = DateTime(required=True, metadata={"example": '2022-02-20T09:59:21.61+00:00'})
    bucketRegion = String(required=True, metadata={"example": 'us-east-1'})
    bucketUrl = String(metadata={"example": 'my-bucket.s3.amazonaws.com'})
    # bucketLifecycle = List(Dict())
    bucketAccess = Nested(
        BucketAccess, metadata={"example": {'status': 'private', 'description': 'All objects are private'}},
    )
    # bucketSize = Dict(
    #     example={'value': 123, 'unit': 'MiB'}
    # )


class BucketPermission(Schema):
    status = String(metadata={"example": 'private'})
    description = String(metadata={"example": 'All objects are private'})
    bucketACL = String(metadata={"example": 'private'})
    pubBlockConfig = Dict(metadata={"example": {
            'isBlockNewAcls': True,
            'isBlockAllAcls': True,
            'isBlockNewPolicy': True,
            'isBlockAllPolicy': True,
        }}
    )


class BucketProperty(Schema):
    isEncryption = Boolean(required=True, metadata={"example": False})
    isVersioning = Boolean(required=True, metadata={"example": False})


class BucketDetail(Schema):
    bucketBasic = Nested(BucketBasic)
    bucketPermission = Nested(BucketPermission)
    bucketProperty = Nested(BucketProperty)
    bucketSize = Dict(metadata={"example": {'value': 123, 'unit': 'KiB'}})
    userTags = Nested(TagItem(many=True))


class ObjectKeyQuery(Schema):
    dc = String(required=True, metadata={"example": 'Easyun'})
    key = String(required=True)


class ObjectContents(Schema):
    key = String(metadata={"example": 'demofile.txt'})
    size = Integer(metadata={"example": 10240})
    key = String(metadata={"example": 'demofile.txt'})
    type = String(metadata={"example": 'Text File'})
    storageClass = String(metadata={"example": 'STANDARD'})
    modifiedTime = DateTime(required=True, metadata={"example": '2022-02-20T09:59:21.61+00:00'})
    # eTag = String(example='99fcf0a51590c45d9dc0687a732ff500')


class VolAttachment(Schema):
    svrId = String(required=True, metadata={"example": 'i-09aa9e2c83d840ab1'})
    tagName = String(metadata={"example": 'test-devbk'})
    attachPath = String(required=True, metadata={"example": '/dev/sdf'})
    diskType = String(metadata={"example": 'user'})
    attachTime = DateTime(metadata={"example": '2022-02-27T02:20:44+00:00'})


class VolumeConfig(Schema):
    volumeSize = Integer(metadata={"example": 10})
    volumeIops = Integer(metadata={"example": 3000})
    volumeThruput = Integer(metadata={"example": 500})
    isEncrypted = Boolean(metadata={"example": False})


class VolumeBasic(Schema):
    volumeId = String(required=True, metadata={"example": 'vol-0bd70f2001d6fb8bc'})
    tagName = String(metadata={"example": 'disk_test'})
    isAttachable = Boolean(metadata={"example": False})
    volumeState = String(metadata={"example": 'in-use'})
    volumeAz = String(metadata={"example": 'us-east-1a'})
    volumeType = String(metadata={"example": 'gp3'})
    volumeSize = Integer(metadata={"example": 10})
    createTime = DateTime(
        # 效果同 .isoformat()
        metadata={"example": '2022-02-20T09:59:21.61+00:00'}
    )


class VolumeModel(Schema):
    volumeId = String(required=True, metadata={"example": 'vol-0bd70f2001d6fb8bc'})
    tagName = String(metadata={"example": 'disk_test'})
    volumeState = String(metadata={"example": 'in-use'})
    isAttachable = Boolean(metadata={"example": False})
    volumeAz = String(metadata={"example": 'us-east-1a'})
    createTime = DateTime(
        # 效果同 .isoformat()
        metadata={"example": '2022-02-20T09:59:21.61+00:00'}
    )
    volumeType = String(metadata={"example": 'gp3'})
    volumeSize = Integer(metadata={"example": 10})
    volumeIops = Integer(metadata={"example": 3000})
    volumeThruput = Integer(metadata={"example": 500})
    isEncrypted = Boolean(metadata={"example": False})
    isMultiAttach = Boolean(metadata={"example": False})
    volumeAttach = Nested(VolAttachment(many=True))


class VolumeDetail(Schema):
    volumeBasic = Nested(VolumeBasic)
    volumeConfig = Nested(VolumeConfig)
    volumeAttach = Nested(VolAttachment(many=True))
    userTags = Nested(TagItem(many=True))


class AddVolumeParm(Schema):
    dcName = String(required=True, metadata={"example": 'Easyun'})
    svrId = String(metadata={"example": 'i-0ac436622e8766a13'})  # 云服务器ID
    attachPath = String(metadata={"example": '/dev/sdf'})
    # volume create params
    volumeSize = Integer(required=True, metadata={"example": 10})
    volumeType = String(
        required=True,
        validate=OneOf(VOLUME_TYPES), metadata={"example": 'gp3'}
    )
    isEncrypted = Boolean(metadata={"example": False})
    isMultiAttach = Boolean(metadata={"example": False})
    volumeIops = Integer(metadata={"example": 3000})
    volumeThruput = Integer(metadata={"example": 500})
    azName = String(metadata={"example": 'us-east-1a'})
    tagName = String(metadata={"example": 'disk_test'})


class DelVolumeParm(Schema):
    dcName = String(required=True, metadata={"example": 'Easyun'})
    volumeIds = List(
        String(),
        required=True, metadata={"example": ['vol-05b06708c63dce7d9', ]},
    )


class AttachVolParm(Schema):
    volumeId = String(required=True, metadata={"example": 'vol-05b06708c63dce7d9'})
    svrId = String(required=True, metadata={"example": 'i-0ac436622e8766a13'})  # 云服务器ID
    attachPath = String(metadata={"example": '/dev/sdf'})


class DetachVolParm(Schema):
    volumeId = String(required=True, metadata={"example": 'vol-05b06708c63dce7d9'})
    svrId = String(required=True, metadata={"example": 'i-0ac436622e8766a13'})  # 云服务器ID
    attachPath = String(metadata={"example": '/dev/sdf'})
