# encoding: utf-8
"""
  @module:  Datacenter module Schema
  @desc:    Datacenter Input/output schema
  @author:  shui, aleck
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited.
"""

from apiflask import Schema
from apiflask.fields import String, List, Dict, DateTime, Boolean, Nested, Number, Field
from apiflask.validators import Length, OneOf, Regexp
from easyun.common.schemas import TagItem
from easyun.cloud.aws_region import get_region_codes


# 定义获取DC默认值的query参数
class DefaultParmQuery(Schema):
    '''datacenter name for query parm'''

    dc = String(required=True, validate=Length(0, 30), example='Easyun')
    region = String(validate=OneOf(get_region_codes()), example='us-east-1')


# 定义VPC 参数的格式
class VpcParm(Schema):
    cidrBlock = String(  # VPC IPv4 address range
        required=True, validate=Length(0, 20), example="10.15.1.0/24"
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
    enablePing = Boolean(required=True, example=False)
    enableSSH = Boolean(required=True, example=False)
    enableRDP = Boolean(required=True, example=False)


# 定义Subnet参数的格式 (just for test)
class SubnetParm(Schema):
    tagName = String(required=True, validate=Length(0, 256), example="Public subnet 1")
    cidrBlock = String(required=True, validate=Length(0, 20), example="10.15.1.0/24")
    azName = String(required=True, validate=Length(0, 20), example="us-east-1a")
    gwName = String(required=True, validate=Length(0, 20), example="easyun-igw")
    routeTable = String(required=True, validate=Length(0, 30), example="easyun-rtb-igw")
    # subnetType = String(
    #     validate=OneOf(['public', 'private']),
    #     example="public"
    # )


# 定义新建Datacenter 传参格式
DATACENTER_NANE_PATTERN = "(?!^(\d{1,3}\.){3}\d{1,3}$)(^[a-zA-Z0-9]([a-zA-Z0-9-]*(\.[a-zA-Z0-9])?)*$)"


class AddDataCenterParm(Schema):
    dcName = String(
        required=True,
        validate=[Regexp(DATACENTER_NANE_PATTERN), Length(3, 60)],
        example="Easyun"  # Datacenter name
    )
    dcRegion = String(required=True, validate=Length(0, 20), example="us-east-1")

    dcVPC = Nested(
        VpcParm,
        required=True,
        example={
            "cidrBlock": "10.15.0.0/16",
        },
    )

    pubSubnet1 = Nested(
        SubnetParm,
        required=True,
        example={
            "tagName": "Public subnet 1",
            "azName": "us-east-1b",
            "cidrBlock": "10.15.1.0/24",
            "gwName": "easyun-igw",
            "routeTable": "easyun-rtb-igw",
        },
    )
    pubSubnet2 = Nested(
        SubnetParm,
        required=True,
        example={
            "tagName": "Public subnet 2",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.2.0/24",
            "gwName": "easyun-igw",
            "routeTable": "easyun-rtb-igw",
        },
    )
    priSubnet1 = Nested(
        SubnetParm,
        required=True,
        example={
            "tagName": "Private subnet 1",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.21.0/24",
            "gwName": "easyun-natgw",
            "routeTable": "easyun-rtb-nat",
        },
    )
    priSubnet2 = Nested(
        SubnetParm,
        required=True,
        example={
            "tagName": "Private subnet 2",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.22.0/24",
            "gwName": "easyun-natgw",
            "routeTable": "easyun-rtb-nat",
        },
    )

    securityGroup0 = Nested(
        SecGroupParm,
        required=True,
        example={
            "tagName": "easyun-sg-default",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False,
        },
    )
    securityGroup1 = Nested(
        SecGroupParm,
        required=True,
        example={
            "tagName": "easyun-sg-webapp",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False,
        },
    )
    securityGroup2 = Nested(
        SecGroupParm,
        required=True,
        example={
            "tagName": "easyun-sg-database",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False,
        },
    )


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
        required=True, validate=Length(0, 60), example="Easyun"  # Datacenter name
    )
    isForceDel = Boolean(example=False)


'''
Schemas for Datacenter APIs
==================================================================
'''


class AddDatacenter(Schema):
    region = String(required=True, validate=Length(0, 20))  # VPC name
    vpc_cidr = String(required=True, validate=Length(0, 20))  # IP address range
    public_subnet_1 = String(required=True)
    public_subnet_2 = String(required=True)
    private_subnet_1 = String(required=True)
    private_subnet_2 = String(required=True)
    sgs1_flag = String(required=True)
    sgs2_flag = String(required=True)
    sgs3_flag = String(required=True)
    keypair = String(required=True)


class DcParmSubnetSchema(Schema):
    """
    DcParm嵌套Schema
    {
                "azName": "us-east-1a",
                "cidrBlock": "10.10.1.0/24",
                "gwName": "easyun-igw",
                "name": "Public subnet 1",
                "routeTable": "easyun-route-igw"
                }
    """

    az = String()
    cidr = String()
    gateway = String()
    name = String()
    route_table = String(data_key='routeTable')


class DcParmSecGroupSchema(Schema):
    """
    DcParm嵌套Schema
    {
        "enableRDP": "true",
        "enablePing": "true",
        "enableSSH": "true",
        "name": "easyun-sg-default"
    }
    """

    enable_RDP = String(data_key='enableRDP')
    enable_Ping = String(data_key='enablePing')
    enable_SSH = String(data_key='enableSSH')
    name = String()


class DcParmIn(Schema):
    region = String(
        required=True, validate=Length(0, 20), example="us-east-1"
    )  # VPC name
    vpc_cidr = String(
        required=True, validate=Length(0, 20), example="10.10.0.0/16"
    )  # IP address range
    priSubnet1 = List(Nested(DcParmSubnetSchema()), required=True)
    priSubnet2 = List(Nested(DcParmSubnetSchema()), required=True)
    pubSubnet1 = List(Nested(DcParmSubnetSchema()), required=True)
    pubSubnet2 = List(Nested(DcParmSubnetSchema()), required=True)

    securityGroup1 = List(Nested(DcParmSecGroupSchema()), required=True)
    securityGroup2 = List(Nested(DcParmSecGroupSchema()), required=True)
    securityGroup3 = List(Nested(DcParmSecGroupSchema()), required=True)
    # keypair = String(required=True, example="key_easyun_user")


class VpcListIn(Schema):
    vpc_id = String(data_key='vpcId')


class DataCenterListIn(Schema):
    dcName = String()


class DataCenterListsIn(Schema):
    dcName = String()
    type = String()


class VpcListOut(Schema):
    vpc_id = String()
    pub_subnet1 = String()
    pub_subnet2 = String()
    private_subnet1 = String()
    private_subnet2 = String()
    sgs = String()
    keypair = String()


# 定义api返回数据格式
class DataCenterBasic(Schema):
    dcName = String(example='Easyun')
    regionCode = String(example='us-east-1')
    vpcID = String(example='vpc-057f0e3d715c24147')


class DataCenterModel(Schema):
    dcName = String(example='Easyun')
    regionCode = String(example='us-east-1')
    vpcID = String(example='vpc-057f0e3d715c24147')
    cidrBlock = String(example='10.10.0.0/16')
    createDate = DateTime()
    createUser = String(example='admin')
    accountId = String(example='567812345678')


'''
Schemas for Subnet APIs
==================================================================
'''


class SubnetBasic(Schema):
    subnetId = String(example='subnet-06bfe659f6ecc2eed')
    subnetState = String(example='available')
    subnetType = String(validate=OneOf(['public', 'private']), example='public')
    cidrBlock = String(example='10.10.1.0/24')
    azName = String(example='us-east-1a')
    tagName = String(example="public_subnet_1")


class SubnetModel(Schema):
    subnetId = String(example='subnet-06bfe659f6ecc2eed')
    subnetState = String(example='available')
    subnetType = String(validate=OneOf(['public', 'private']), example='public')
    cidrBlock = String(example='10.10.1.0/24')
    azName = String(example='us-east-1a')
    tagName = String(example="public_subnet_1")
    vpcId = String(example='vpc-057f0e3d715c24147')
    availableIpNum = Number(example=242)
    isMapPublicIp = Boolean(example=True)


class SubnetDetail(Schema):
    subnetId = String(example='subnet-06bfe659f6ecc2eed')
    subnetState = String(example='available')
    subnetType = String(validate=OneOf(['public', 'private']), example='public')
    cidrBlock = String(example='10.10.1.0/24')
    azName = String(example='us-east-1a')
    tagName = String(example="public_subnet_1")
    vpcId = String(example='vpc-057f0e3d715c24147')    
    availableIpNum = Number(example=242)
    isMapPublicIp = Boolean(example=True)
    serverNum = Number(example=1)
    eniNum = Number(example=3)
    userTags = Nested(TagItem(many=True))


class DelSubnetParm(Schema):
    dcName = String(required=True, example="Easyun")
    subnetId = String(required=True, example='subnet-06bfe659f6ecc2eed')


class AddSubnetParm(Schema):
    dcName = String(required=True, example="Easyun")
    cidrBlock = String(required=True, example='10.10.1.0/24')
    azName = String(required=True, example='us-east-1a')
    tagName = String(example="Secgroup_for_Web")


'''
Schemas for RouteTable APIs
==================================================================
'''


class RouteTableBasic(Schema):
    rtbId = String(example='rtb-040ac5d25869f45ab')
    tagName = String(example="route-nat-easyun")
    vpcId = String(example='vpc-057f0e3d715c24147')


class RouteTableModel(Schema):
    rtbId = String(example='rtb-040ac5d25869f45ab')
    tagName = String(example="route-nat-easyun")
    vpcId = String(example='vpc-057f0e3d715c24147')
    associations = List(Dict)
    routes = List(Dict)
    propagateVgws = List(Dict)


class RouteTableDetail(Schema):
    rtbId = String(example='rtb-040ac5d25869f45ab')
    tagName = String(example="route-nat-easyun")
    vpcId = String(example='vpc-057f0e3d715c24147')
    associations = List(Dict)
    routes = List(Dict)
    propagateVgws = List(Dict)
    userTags = Nested(TagItem(many=True))


class DelRouteTableParm(Schema):
    dcName = String(required=True, example="Easyun")
    subnetId = String(required=True, example='subnet-06bfe659f6ecc2eed')


class AddRouteTableParm(Schema):
    dcName = String(required=True, example="Easyun")
    cidrBlock = String(required=True, example='10.10.1.0/24')
    azName = String(required=True, example='us-east-1a')
    tagName = String(example="Secgroup_for_Web")


'''
Schemas for StaticIP(Eip) APIs
==================================================================
'''


class StaticIPBasic(Schema):
    eipId = String()
    publicIp = String()
    tagName = String(example="web_staticip")
    associationId = String()
    isAvailable = Boolean(example=True)


class StaticIPModel(Schema):
    eipId = String()
    publicIp = String()
    tagName = String(example="web_staticip")
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
    dcName = String(required=True, example="Easyun")
    eipId = String(required=True, example="eipalloc-0fdb6c5e3a254c937")


'''
Schemas for SecGropu APIs
==================================================================
'''


class IpPermission(Schema):
    FromPort = Number(example=3306)
    ToPort = Number(example=3306)
    IpProtocol = String(required=True, example='tcp')
    IpRanges = List(Dict())
    Ipv6Ranges = List(Dict())
    PrefixListIds = List(Dict())
    UserIdGroupPairs = List(Dict())


class SecGroupBasic(Schema):
    sgId = String(required=True, example="sg-05df5c8e8396d06e9")
    sgName = String(example="easyun-sg-web")
    tagName = String(example="Secgroup_for_Web")
    sgDesc = String(example="allow web application")


class SecGroupModel(Schema):
    sgId = String(required=True, example="sg-05df5c8e8396d06e9")
    sgName = String(example="easyun-sg-web")
    tagName = String(example="Secgroup_for_Web")
    sgDesc = String(example="allow web application")
    # Inbound Ip Permissions
    ibRulesNum = Number(example=3)
    ibPermissions = List(Dict())
    # Outbound Ip Permissions
    obRulesNum = Number(example=1)
    obPermissions = List(Dict())


class SecGroupDetail(Schema):
    sgBasic = Nested(SecGroupBasic)


class DelSecGroupParm(Schema):
    dcName = String(required=True, example="Easyun")
    sgId = String(required=True, example="sg-05df5c8e8396d06e9")


class AddSecGroupParm(Schema):
    dcName = String(required=True, example="Easyun")
    sgName = String(required=True, example="easyun-sg-web")
    sgDesc = String(required=True, example="allow web application")    
    tagName = String(example="Secgroup_for_Web")


'''
Schemas for Gateway APIs
==================================================================
'''


class AddIntGateway(Schema):
    dcName = String(required=True, example="Easyun") 
    tagName = String(example="Easyun_Internet_Gateway")


class AddNatGateway(Schema):
    dcName = String(required=True, example="Easyun")
    connectType = String(required=True, example="easyun-sg-web")
    subnetId = String(required=True, example='subnet-06bfe659f6ecc2eed')
    allocationId = String(required=True, example='allo-xxxxxx')
    tagName = String(example="Easyun_NAT_Gateway")
