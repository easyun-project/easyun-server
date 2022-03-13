# encoding: utf-8
"""
  @module:  Datacenter module Schema
  @desc:    Datacenter Input/output schema
  @author:  shui, aleck
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited.    
"""

from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String, List, Dict, DateTime, Boolean, Nested
from apiflask.validators import Length, OneOf



# 定义VPC 参数的格式
class VpcParm(Schema):
    cidrBlock = String(               #VPC IPv4 address range
        required=True, validate=Length(0, 20),
        example="10.15.1.0/24"
    )
    cidrBlockv6 = String(             #VPC IPv6 address range
        required=False, validate=Length(0, 128),
    )
    vpcTenancy = String(
        required=False, validate=OneOf('Default', 'Dedicated'),
    )

# 定义Security Group参数的格式
class SecGroupParm(Schema):
    tagName = String(
        required=True,
        validate=Length(0, 20)
    )
    enablePing = Boolean(required=True, example=False)
    enableSSH = Boolean(required=True, example=False)
    enableRDP = Boolean(required=True, example=False)


# 定义Subnet参数的格式 (just for test)
class SubnetParm(Schema):
    tagName = String(
        required=True,
        validate=Length(0, 40),
        example="Public subnet 1"
    )
    cidrBlock = String(
        required=True,
        validate=Length(0, 20),
        example="10.15.1.0/24"
    )
    azName = String(
        required=True,
        validate=Length(0, 20),
        example="us-east-1a"
    )    
    gwName = String(
        required=True,
        validate=Length(0, 20),
        example="easyun-igw"
    )
    routeTable = String(
        required=True,
        validate=Length(0, 30),
        example="easyun-rtb-igw"
    )
    # subnetType = String(
    #     validate=OneOf(['public', 'private']),
    #     example="public"
    # )

# 定义新建Datacenter 传参格式
class CreateDcParms(Schema):
    dcName = String(required=True,   #Datacenter name
        validate=Length(0, 60),
        example="Easyun"
    )
    dcRegion = String(required=True, 
        validate=Length(0, 20),
        example="us-east-1"
    )
             
    dcVPC = Nested(VpcParm, required=True,
        example={
            "cidrBlock": "10.15.0.0/16",
        }
    )
    
    pubSubnet1 = Nested(SubnetParm, required=True,
        example={
            "tagName": "Public subnet 1",
            "azName": "us-east-1b",
            "cidrBlock": "10.15.1.0/24",
            "gwName": "easyun-igw",
            "routeTable": "easyun-rtb-igw"
        }
    )
    pubSubnet2 = Nested(SubnetParm, required=True,
        example={
            "tagName": "Public subnet 2",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.2.0/24",
            "gwName": "easyun-igw",                
            "routeTable": "easyun-rtb-igw"
        }
    )
    priSubnet1 = Nested(SubnetParm, required=True,
        example={
            "tagName": "Private subnet 1",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.21.0/24",
            "gwName": "easyun-natgw",
            "routeTable": "easyun-rtb-nat"
        }
    )
    priSubnet2 = Nested(SubnetParm, required=True,
        example={
            "tagName": "Private subnet 2",
            "azName": "us-east-1c",
            "cidrBlock": "10.15.22.0/24",
            "gwName": "easyun-natgw",                
            "routeTable": "easyun-rtb-nat"
        }
    )

    securityGroup0 = Nested(SecGroupParm, required=True,
        example={   
            "tagName": "easyun-sg-default",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        }
    )
    securityGroup1 = Nested(SecGroupParm, required=True,
        example={   
            "tagName": "easyun-sg-webapp",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        }
    )
    securityGroup2 = Nested(SecGroupParm, required=True,
        example={   
            "tagName": "easyun-sg-database",
            "enablePing": True,
            "enableSSH": True,
            "enableRDP": False
        }
    )


# 定义api返回数据格式
class CreateDcResult(Schema):
    name = String()
    cloud= String()     
    region = String()
    vpc_id = String()
    create_date = DateTime()

''' 
Schemas for Datacenter APIs
==================================================================
'''

class AddDatacenter(Schema):
    region = String(required=True, validate=Length(0, 20))     #VPC name
    vpc_cidr = String(required=True, validate=Length(0, 20))     #IP address range
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


class DcParmPsecurityGroupSchema(Schema):
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
    region = String(required=True, validate=Length(0, 20), example="us-east-1")     #VPC name
    vpc_cidr = String(required=True, validate=Length(0, 20), example="10.10.0.0/16")     #IP address range
    priSubnet1 = List(
        Nested(DcParmSubnetSchema()),
        required=True
    )
    priSubnet2 = List(
        Nested(DcParmSubnetSchema()),
        required=True
    )
    pubSubnet1 = List(
        Nested(DcParmSubnetSchema()),
        required=True
     )
    pubSubnet2 = List(
        Nested(DcParmSubnetSchema()),
        required=True
     )

    securityGroup1 = List(
        Nested(DcParmPsecurityGroupSchema()),
        required=True
     )
    securityGroup2 = List(
        Nested(DcParmPsecurityGroupSchema()),
        required=True
     )
    securityGroup3 = List(
        Nested(DcParmPsecurityGroupSchema()),
        required=True
     )
    # keypair = String(required=True, example="key_easyun_user")



class DataCenterResultOut(Schema):
    region_name = String(data_key='regionName')
    vpc_id = String(data_key='vpcId')


class VpcListIn(Schema):
    vpc_id = String(data_key='vpcId')


class VpcListOut(Schema):
    vpc_id = String()
    pub_subnet1 = String()
    pub_subnet2 = String()
    private_subnet1 = String()
    private_subnet2 = String()
    sgs = String()
    keypair = String()


class DataCenterListIn(Schema):
    dcName = String()


class DataCenterListsIn(Schema):
    dcName = String()
    type = String()



''' 
Schemas for Eip APIs
==================================================================
'''

class DelEipParm(Schema):
    dcName = String(
        required=True,
        example= "Easyun")
    alloId = String(
        required=True,
        example= "eipalloc-0fdb6c5e3a254c937")
    pubIp = String(
        required=False,
        example= "12.34.56.78")        


class DataCenterEIPIn(Schema):
    dcName = String()
    alloId = String()

class DataCenterNewEIPIn(Schema):
    dcName = String()

class DCInfoOut(Schema):
    dcName = String()
    dcRegion = String()
    rgName = String()			
    vpcID = String()
    vpcCidr = String()
    dcUser = String()
    dcAccount = String()

class DataCenterSubnetIn(Schema):
    dcName = String()
    subnetID = String()

class DataCenterSubnetInsert(Schema):
    dcName = String()
    subnetCDIR = String() 

class DataCenterListOut(Schema):
    dcList = List(
        Nested(DCInfoOut),
        example = [
            {
                "dcName" : "Easyun",
                "dcRegion" : "us-east-1",
                # "rgName" : "US East (N. Virginia)",			
                "vpcID" : "vpc-04b38448e58d715c2",
                "vpcCidr" : "10.10.0.0/16",
                "dcUser" : "admin",
                "dcAccount" : "565521295678"
            }
        ]
    )

class ResourceListOut(Schema):
    """
    默认返回参数
    """
    region = String()
    az = String()
    key = String()
    vpc_cidr = String(data_key='vpcCidr')
    pub_subnet1 = String(data_key='pubSubnet1')
    pub_subnet2 = String(data_key='pubSubnet2')
    pri_subnet1 = String(data_key='priSubnet1')
    pri_subnet2 = String(data_key='priSubnet2')
    secure_group1 = String(data_key='secureGroup1')
    secure_group2 = String(data_key='secureGroup2')
    secure_group3 = String(data_key='secureGroup3')
    tag_spec = List(Dict, data_key='tagSpec')