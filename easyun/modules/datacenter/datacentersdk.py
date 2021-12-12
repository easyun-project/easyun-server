# -*- coding: utf-8 -*-
"""
  @author:  pengchang
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited. 
  @file:    datacenter_add.py
  @desc:    The DataCenter Create module
"""

from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import jsonify
from datetime import date, datetime
from easyun.common.auth import auth_token
from easyun.common.models import Account,Datacenter
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun import db
import boto3
import os, time
import json
from . import TagEasyun

class datacentersdk():
    def add_subnet(ec2,vpc,route_table,subnet):
            TagEasyunSubnet= [{'ResourceType':'subnet','Tags': TagEasyun}]

            subnet = ec2.create_subnet(CidrBlock=subnet, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
            # associate the route table with the subnet
            route_table.associate_with_subnet(SubnetId=subnet['Subnet']['SubnetId'])
            print('Public subnet1= '+ subnet['Subnet']['SubnetId'])


    def add_VPC_security_group(ec2,vpc,groupname,description,IpPermissions):
        TagEasyunSecurityGroup= [{'ResourceType':'security-group','Tags': TagEasyun}]
        
        secure_group = ec2.create_security_group(GroupName=groupname, Description=description, VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
        
        ec2.authorize_security_group_ingress(
            GroupId=secure_group['GroupId'],
            IpPermissions=IpPermissions)
        
        print('secure_group2= '+secure_group['GroupId'])


    def add_VPC_db(vpc,region):
        new_datacenter = Datacenter(id=1,name='Easyun',cloud='AWS', account='', region=region,vpc_id=vpc.id,credate=datetime.date())
        db.session.add(new_datacenter)
        


    def view_func(request):
        # 增
        new_datacenter = Datacenter(id=1, region='test')
        db.session.add(new_datacenter)

        # 查
        datacenter = Datacenter.query.filter(id=1).first()

        # 修改
        datacenter.region = 'new_test'
        db.session.commit()
