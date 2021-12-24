#!/usr/bin/env python
# encoding: utf-8
"""
  @author:  shui
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited. 
  @file:    schemas.py
  @desc:
"""
from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from marshmallow.fields import Nested


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


class DcParmIn(Schema):
    region = String(required=True, validate=Length(0, 20),
        example="us-east-1")     #VPC name
    vpc_cidr = String(required=True, validate=Length(0, 20),
        example="10.10.0.0/16")     #IP address range
    priSubnet1 = List(
        Dict(
            example={
                "az": "us-east-1a",
                "cidr": "10.10.21.0/24",
                "gateway": "easyun-igw",
                "name": "Private subnet 1",
                "routeTable": "easyun-route-nat"
                }
        ),
        required=True
    )
    priSubnet2 = List(
        Dict(
            example={
                "az": "us-east-1b",
                "cidr": "10.10.22.0/24",
                "gateway": "easyun-igw",
                "name": "Private subnet 2",
                "routeTable": "easyun-route-nat"
                }
        ),
        required=True
    )
    pubSubnet1 = List(
        Dict(
            example={
                "az": "us-east-1a",
                "cidr": "10.10.1.0/24",
                "gateway": "easyun-igw",
                "name": "Public subnet 1",
                "routeTable": "easyun-route-igw"
                }
        ),
        required=True
     )
    pubSubnet2 = List(
        Dict(
            example={
                "az": "us-east-1b",
                "cidr": "10.10.2.0/24",
                "gateway": "easyun-igw",
                "name": "Public subnet 2",
                "routeTable": "easyun-route-igw"
                }
        ),
        required=True
     )
    pubSubnet2 = List(
        Dict(
            example={
                "az": "us-east-1b",
                "cidr": "10.10.2.0/24",
                "gateway": "easyun-igw",
                "name": "Public subnet 2",
                "routeTable": "easyun-route-igw"
                }
        ),
        required=True
     )

    securityGroup1 = List(
        Dict(
            example={   
                    "enableRDP": "true",
                    "enablePing": "true",
                    "enableSSH": "true",
                    "name": "easyun-sg-default"
                      }
        ),
        required=True
     )
    securityGroup2 = List(
        Dict(
            example={   
                    "enableRDP": "true",
                    "enablePing": "true",
                    "enableSSH": "true",
                    "name": "easyun-sg-webapp"
                      }
        ),
        required=True
     )
    securityGroup3 = List(
        Dict(
            example={   
                    "enableRDP": "true",
                    "enablePing": "true",
                    "enableSSH": "true",
                    "name": "easyun-sg-database"
                      }
        ),
        required=True
     )
    keypair = String(required=True,
        example="key_easyun_user")


class DataCenterResultOut(Schema):
    region_name = String()
    vpc_id = String()


class VpcListIn(Schema):
    vpc_id = String()


class VpcListOut(Schema):
    vpc_id = String()
    pub_subnet1 = String()
    pub_subnet2 = String()
    private_subnet1 = String()
    private_subnet2 = String()
    sgs = String()
    keypair = String()


class DataCenterListIn(Schema):
    vpc_id = String()




class DCInfoOut(Schema):
    dcName = String()
    dcRegion = String()
    rgName = String()			
    vpcID = String()
    vpcCidr = String()
    dcUser = String()
    dcAccount = String()

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