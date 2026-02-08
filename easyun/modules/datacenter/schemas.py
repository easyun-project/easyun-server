# encoding: utf-8
"""
  @module:  Datacenter module Schema
  @desc:    Datacenter Input/output schema
  @author:  shui, aleck
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited.
"""

from apiflask import Schema
from apiflask.fields import String, List, Dict, DateTime, Boolean, Nested, Integer, Field
from apiflask.validators import Length, OneOf, Regexp
from easyun.common.schemas import TagItem
from easyun.cloud.aws_region import get_region_codes


# 定义获取DC默认值的query参数
class DefaultParmQuery(Schema):
    '''datacenter name for query parm'''

    dc = String(required=True, validate=Length(0, 30), metadata={"example": 'Easyun'})
    region = String(validate=OneOf(get_region_codes()), metadata={"example": 'us-east-1'})


# 定义VPC 参数的格式
class VpcParm(Schema):
    cidrBlock = String(  # VPC IPv4 address range
        required=True, validate=Length(0, 20), metadata={"example": "10.15.1.0/24"}
    )
    cidrBlockv6 = String(  # VPC IPv6 address range
        required=False,
        validate=Length(0, 128),
    )
    vpcTenancy = String(
        required=False,
        validate=OneOf('Default', 'Dedicated'),
    )


# 定义Security Group参数的格式
class SecGroupParm(Schema):
    tagName = String(required=True, validate=Length(0, 256))
    enablePing = Boolean(required=True, metadata={"example": False})
    enableSSH = Boolean(required=True, metadata={"example": False})
    enableRDP = Boolean(required=True, metadata={"example": False})


# 定义Subnet参数的格式 (just for test)
class SubnetParm(Schema):
    tagName = String(required=True, validate=Length(0, 256), metadata={"example": "Public subnet 1"})
    cidrBlock = String(required=True, validate=Length(0, 20), metadata={"example": "10.15.1.0/24"})
    azName = String(required=True, validate=Length(0, 20), metadata={"example": "us-east-1a"})
    gwName = String(required=True, validate=Length(0, 20), metadata={"example": "easyun-igw"})
    routeTable = String(required=True, validate=Length(0, 30), metadata={"example": "easyun-rtb-igw"})
    # subnetType = String(
    #     validate=OneOf(['public', 'private']),
    #     example="public"
    # )


# 定义新建Datacenter 传参格式
DATACENTER_NANE_PATTERN = "(?!^(\d{1,3}\.){3}\d{1,3}$)(^[a-zA-Z0-9]([a-zA-Z0-9-]*(\.[a-zA-Z0-9])?)*$)"


class AddDataCenterParm(Schema):
    dcName = String(
        required=True,
        validate=[Regexp(DATACENTER_NANE_PATTERN), Length(3, 60)], metadata={"example": "Easyun"}  # Datacenter name
    )
    dcRegion = String(required=True, validate=Length(0, 20), metadata={"example": "us-east-1"})

    dcVPC = Nested(
        VpcParm,
        required=True, metadata={"example": {
            "cidrBlock": "10.15.0.0/16",
        }},
    )

    pubSubnet1 = Nested(
        SubnetParm,
        required=True, metadata={"example": {
            "tagName": "Public subnet 1",
            "azName": "us-east-1b",
            "cidrBlock": "10.15.1.0/24",
            "gwName": "easyun-igw",
            "routeTable": "easyun-rtb-igw",
        }},
    )
    pubSubnet2 = Nested(
        SubnetParm,
        required=True, metadata={"example": {
            "tagName": "Public subnet 2",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.2.0/24",
            "gwName": "easyun-igw",
            "routeTable": "easyun-rtb-igw",
        }},
    )
    priSubnet1 = Nested(
        SubnetParm,
        required=True, metadata={"example": {
            "tagName": "Private subnet 1",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.21.0/24",
            "gwName": "easyun-natgw",
            "routeTable": "easyun-rtb-nat",
        }},
    )
    priSubnet2 = Nested(
        SubnetParm,
        required=True, metadata={"example": {
            "tagName": "Private subnet 2",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.22.0/24",
            "gwName": "easyun-natgw",
            "routeTable": "easyun-rtb-nat",
        }},
    )

    securityGroup0 = Nested(
        SecGroupParm,
        required=True, metadata={"example": {
            "tagName": "easyun-sg-default",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False,
        }},
    )
    securityGroup1 = Nested(
        SecGroupParm,
        required=True, metadata={"example": {
            "tagName": "easyun-sg-webapp",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False,
        }},
    )
    securityGroup2 = Nested(
        SecGroupParm,
        required=True, metadata={"example": {
            "tagName": "easyun-sg-database",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False,
        }},
    )

    createNatGW = Boolean(load_default=False, metadata={"example": False})


# 定义DC参数返回格式
class DropDownList(Schema):
    azList = List(String)
    gwList = List(String)
    rtbList = List(String)


class DefaultParmsOut(Schema):
    dcParms = Nested(AddDataCenterParm)
    dropDown = Nested(DropDownList)


class DelDataCenterParm(Schema):
    dcName = String(
        required=True, validate=Length(0, 60), metadata={"example": "Easyun"}  # Datacenter name
    )
    isForceDel = Boolean(metadata={"example": False})


'''
Schemas for Datacenter APIs
==================================================================
'''


# 定义api返回数据格式
class DataCenterBasic(Schema):
    dcName = String(metadata={"example": 'Easyun'})
    regionCode = String(metadata={"example": 'us-east-1'})
    vpcID = String(metadata={"example": 'vpc-057f0e3d715c24147'})


class DataCenterModel(Schema):
    dcName = String(metadata={"example": 'Easyun'})
    regionCode = String(metadata={"example": 'us-east-1'})
    vpcID = String(metadata={"example": 'vpc-057f0e3d715c24147'})
    cidrBlock = String(metadata={"example": '10.10.0.0/16'})
    createDate = DateTime()
    createUser = String(metadata={"example": 'admin'})
    accountId = String(metadata={"example": '567812345678'})


'''
Schemas for Subnet APIs
==================================================================
'''


class SubnetBasic(Schema):
    subnetId = String(metadata={"example": 'subnet-06bfe659f6ecc2eed'})
    subnetState = String(metadata={"example": 'available'})
    subnetType = String(validate=OneOf(['public', 'private']), metadata={"example": 'public'})
    cidrBlock = String(metadata={"example": '10.10.1.0/24'})
    azName = String(metadata={"example": 'us-east-1a'})
    tagName = String(metadata={"example": "public_subnet_1"})


class SubnetModel(Schema):
    subnetId = String(metadata={"example": 'subnet-06bfe659f6ecc2eed'})
    subnetState = String(metadata={"example": 'available'})
    subnetType = String(validate=OneOf(['public', 'private']), metadata={"example": 'public'})
    cidrBlock = String(metadata={"example": '10.10.1.0/24'})
    azName = String(metadata={"example": 'us-east-1a'})
    tagName = String(metadata={"example": "public_subnet_1"})
    vpcId = String(metadata={"example": 'vpc-057f0e3d715c24147'})
    availableIpNum = Integer(metadata={"example": 242})
    isMapPublicIp = Boolean(metadata={"example": True})


class SubnetDetail(Schema):
    subnetId = String(metadata={"example": 'subnet-06bfe659f6ecc2eed'})
    subnetState = String(metadata={"example": 'available'})
    subnetType = String(validate=OneOf(['public', 'private']), metadata={"example": 'public'})
    cidrBlock = String(metadata={"example": '10.10.1.0/24'})
    azName = String(metadata={"example": 'us-east-1a'})
    tagName = String(metadata={"example": "public_subnet_1"})
    vpcId = String(metadata={"example": 'vpc-057f0e3d715c24147'})    
    availableIpNum = Integer(metadata={"example": 242})
    isMapPublicIp = Boolean(metadata={"example": True})
    serverNum = Integer(metadata={"example": 1})
    eniNum = Integer(metadata={"example": 3})
    userTags = Nested(TagItem(many=True))


class DelSubnetParm(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    subnetId = String(required=True, metadata={"example": 'subnet-06bfe659f6ecc2eed'})


class AddSubnetParm(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    cidrBlock = String(required=True, metadata={"example": '10.10.1.0/24'})
    azName = String(required=True, metadata={"example": 'us-east-1a'})
    tagName = String(metadata={"example": "Secgroup_for_Web"})


'''
Schemas for RouteTable APIs
==================================================================
'''


class RouteTableBasic(Schema):
    rtbId = String(metadata={"example": 'rtb-040ac5d25869f45ab'})
    tagName = String(metadata={"example": "route-nat-easyun"})
    vpcId = String(metadata={"example": 'vpc-057f0e3d715c24147'})


class RouteTableModel(Schema):
    rtbId = String(metadata={"example": 'rtb-040ac5d25869f45ab'})
    tagName = String(metadata={"example": "route-nat-easyun"})
    vpcId = String(metadata={"example": 'vpc-057f0e3d715c24147'})
    associations = List(Dict)
    routes = List(Dict)
    propagateVgws = List(Dict)


class RouteTableDetail(Schema):
    rtbId = String(metadata={"example": 'rtb-040ac5d25869f45ab'})
    tagName = String(metadata={"example": "route-nat-easyun"})
    vpcId = String(metadata={"example": 'vpc-057f0e3d715c24147'})
    associations = List(Dict)
    routes = List(Dict)
    propagateVgws = List(Dict)
    userTags = Nested(TagItem(many=True))


class DelRouteTableParm(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    subnetId = String(required=True, metadata={"example": 'subnet-06bfe659f6ecc2eed'})


class AddRouteTableParm(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    cidrBlock = String(required=True, metadata={"example": '10.10.1.0/24'})
    azName = String(required=True, metadata={"example": 'us-east-1a'})
    tagName = String(metadata={"example": "Secgroup_for_Web"})


'''
Schemas for StaticIP(Eip) APIs
==================================================================
'''


class StaticIPBasic(Schema):
    eipId = String()
    publicIp = String()
    tagName = String(metadata={"example": "web_staticip"})
    associationId = String()
    isAvailable = Boolean(metadata={"example": True})


class StaticIPModel(Schema):
    eipId = String()
    publicIp = String()
    tagName = String(metadata={"example": "web_staticip"})
    associationId = String()
    eipDomain = String()
    ipv4Pool = String()
    boarderGroup = String()
    assoTarget = Field()


class StaticIPDetail(Schema):
    eipBasic = Nested(StaticIPBasic)
    eipProperty = Field()
    assoTarget = Field()
    userTags = Nested(TagItem(many=True))


class DelEipParm(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    eipId = String(required=True, metadata={"example": "eipalloc-0fdb6c5e3a254c937"})


'''
Schemas for SecGropu APIs
==================================================================
'''


class IpPermission(Schema):
    FromPort = Integer(metadata={"example": 3306})
    ToPort = Integer(metadata={"example": 3306})
    IpProtocol = String(required=True, metadata={"example": 'tcp'})
    IpRanges = List(Dict())
    Ipv6Ranges = List(Dict())
    PrefixListIds = List(Dict())
    UserIdGroupPairs = List(Dict())


class SecGroupBasic(Schema):
    sgId = String(required=True, metadata={"example": "sg-05df5c8e8396d06e9"})
    sgName = String(metadata={"example": "easyun-sg-web"})
    tagName = String(metadata={"example": "Secgroup_for_Web"})
    sgDesc = String(metadata={"example": "allow web application"})


class SecGroupModel(Schema):
    sgId = String(required=True, metadata={"example": "sg-05df5c8e8396d06e9"})
    sgName = String(metadata={"example": "easyun-sg-web"})
    tagName = String(metadata={"example": "Secgroup_for_Web"})
    sgDesc = String(metadata={"example": "allow web application"})
    # Inbound Ip Permissions
    ibRulesNum = Integer(metadata={"example": 3})
    ibPermissions = List(Dict())
    # Outbound Ip Permissions
    obRulesNum = Integer(metadata={"example": 1})
    obPermissions = List(Dict())


class SecGroupDetail(Schema):
    sgBasic = Nested(SecGroupBasic)


class DelSecGroupParm(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    sgId = String(required=True, metadata={"example": "sg-05df5c8e8396d06e9"})


class AddSecGroupParm(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    sgName = String(required=True, metadata={"example": "easyun-sg-web"})
    sgDesc = String(required=True, metadata={"example": "allow web application"})    
    tagName = String(metadata={"example": "Secgroup_for_Web"})


'''
Schemas for Gateway APIs
==================================================================
'''


class AddIntGateway(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"}) 
    tagName = String(metadata={"example": "Easyun_Internet_Gateway"})


class AddNatGateway(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    connectType = String(required=True, metadata={"example": "easyun-sg-web"})
    subnetId = String(required=True, metadata={"example": 'subnet-06bfe659f6ecc2eed'})
    allocationId = String(required=True, metadata={"example": 'allo-xxxxxx'})
    tagName = String(metadata={"example": "Easyun_NAT_Gateway"})
