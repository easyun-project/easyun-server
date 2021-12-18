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


class DataCenterListOut(Schema):
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



class DataCenter2ListOut(Schema):
    region_name = String()
    vpc_id = String()
    azs = List(String)
    subnets = List(String)
    securitygroup = List(String)
    keypair = List(String)
    create_date = String()