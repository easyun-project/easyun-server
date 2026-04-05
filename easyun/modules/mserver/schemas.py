# encoding: utf-8
"""
  @module:  Server Schema
  @desc:    Server Input/output schema
  @author:  aleck
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested, Float, Boolean
from apiflask.validators import Length, OneOf


class SvrIdParm(Schema):
    svrId = String(  # 云服务器ID
        required=True, metadata={"example": [
            "i-0e7105687e0fec039",
        ]},
    )


class ModSvrNameParm(Schema):
    svrIds = List(  # 云服务器IDs
        String(), required=True, metadata={"example": ['i-0e5250487e0fec039', 'i-0dfc0232b2f4f8ab9']}
    )
    svrName = String(required=True, metadata={"example": 'new_server_name'})  # 云服务器新Name


class ModSvrProtectionParm(Schema):
    svrIds = List(  # 云服务器IDs
        String(), required=True, metadata={"example": ['i-0e5250487e0fec039', 'i-0dfc0232b2f4f8ab9']}
    )
    action = String(
        required=True, validate=OneOf(['enable', 'disable'])  # Operation TYPE
    )


class SvrIdList(Schema):
    svrIds = List(  # 云服务器ID
        String(), required=True, metadata={"example": ['i-0e5250487e0fec039', 'i-0dfc0232b2f4f8ab9']}
    )


# 定义api返回格式 Schema，以Out结尾
class SvrOperateOut(Schema):
    svrId = List(String)
    currState = List(String)
    preState = List(String)


class SvrTagNameItem(Schema):
    svrId = String(metadata={"example": [
            "i-0e7105687e0fec039",
        ]}
    )
    tagName = String(metadata={"example": 'server_name'})


# ---- server list/detail output schemas ----

class SvrDetailItem(Schema):
    svrId = String(metadata={"example": "i-0e7105687e0fec039"})
    tagName = String(metadata={"example": "my-server"})
    svrState = String(metadata={"example": "running"})
    insType = String(metadata={"example": "t3.micro"})
    vpuNum = Integer(metadata={"example": 2})
    ramSize = Float(metadata={"example": 1.0})
    volumeSize = Integer(metadata={"example": 30})
    osName = String(metadata={"example": "Linux/UNIX"})
    azName = String(metadata={"example": "us-east-1a"})
    pubIp = String(metadata={"example": "54.123.45.67"})
    priIp = String(metadata={"example": "10.0.1.100"})
    isEip = Boolean()


class SvrBriefItem(Schema):
    svrId = String(metadata={"example": "i-0e7105687e0fec039"})
    tagName = String(metadata={"example": "my-server"})
    svrState = String(metadata={"example": "running"})
    insType = String(metadata={"example": "t3.micro"})
    azName = String(metadata={"example": "us-east-1a"})


class SvrPropertyOut(Schema):
    instanceName = String()
    instanceType = String()
    vCpu = Integer()
    memory = Float()
    privateIp = String()
    publicIp = String()
    isEip = Boolean()
    status = String()
    instanceId = String()
    launchTime = String()
    privateIpv4Dns = String()
    publicIpv4Dns = String()
    platformDetails = String()
    virtualization = String()
    tenancy = String()
    usageOperation = String()
    monitoring = String()
    terminationProtection = String()
    amiId = String()
    amiName = String()
    amiPath = String()
    keyPairName = String()
    iamRole = String()


class SvrConfigOut(Schema):
    arch = String(metadata={"example": "x86_64"})
    os = String(metadata={"example": "amzn2"})


class SvrSecGroupItem(Schema):
    sgId = String(metadata={"example": "sg-0bb69bb599b303a1e"})
    sgName = String(metadata={"example": "default"})


class SvrEntityOut(Schema):
    svrProperty = Nested(SvrPropertyOut)
    svrConfig = Nested(SvrConfigOut)
    svrDisk = Dict()
    svrNetworking = Dict()
    svrSecurity = List(Nested(SvrSecGroupItem))
    svrTags = List(Dict())
    svrConnect = Dict()


class SvrInstypeParam(Schema):
    insArch = String(metadata={"example": "x86_64"})
    insHyper = String(metadata={"example": "xen"})
    insType = String(metadata={"example": "t3.micro"})
    imgID = String(metadata={"example": "ami-0abcdef1234567890"})


# ---- server param output schemas ----

class ImageItem(Schema):
    imgID = String(metadata={"example": "ami-0abcdef1234567890"})
    osName = String(metadata={"example": "Amazon Linux 2"})
    osVersion = String(metadata={"example": "2.0"})
    osCode = String(metadata={"example": "amzn2"})
    imgDescription = String()
    rootDevice = Dict()


class InsFamilyItem(Schema):
    catgName = String(metadata={"example": "General Purpose"})
    catdesCode = String(metadata={"example": "general"})
    familyName = String(metadata={"example": "m5"})
    familyDes = String(metadata={"example": "General purpose"})


class InsTypeItem(Schema):
    insType = String(metadata={"example": "m5.large"})
    vcpuNum = Integer(metadata={"example": 2})
    memSize = Float(metadata={"example": 8.0})
    netSpeed = String(metadata={"example": "Up to 10 Gigabit"})
    monthPrice = Float(metadata={"example": 69.12})


class InsTypeBriefItem(Schema):
    insType = String(metadata={"example": "m5.large"})
    familyName = String(metadata={"example": "m5"})
    familyDes = String(metadata={"example": "General purpose"})


# ---- server write operation output schemas ----

class NewSvrItem(Schema):
    svrId = String(metadata={"example": "i-0e7105687e0fec039"})
    insTpye = String(metadata={"example": "t3.nano"})
    createTime = String()
    svrState = String(metadata={"example": "pending"})
    priIp = String(metadata={"example": "10.0.1.100"})


class SvrStateChangeItem(Schema):
    svrId = String(metadata={"example": "i-0e7105687e0fec039"})
    currState = String(metadata={"example": "shutting-down"})
    preState = String(metadata={"example": "running"})


class SvrProtectionOut(Schema):
    success = List(String())
    failed = List(String())


class MsgOut(Schema):
    msg = String(metadata={"example": "operation success"})
