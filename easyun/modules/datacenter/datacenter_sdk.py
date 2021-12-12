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
        print('entered add_subnet')
        TagEasyunSubnet= [{'ResourceType':'subnet','Tags': TagEasyun}]

        subnet = ec2.create_subnet(CidrBlock=subnet, VpcId=vpc.id,TagSpecifications=TagEasyunSubnet)
        # associate the route table with the subnet
        route_table.associate_with_subnet(SubnetId=subnet['Subnet']['SubnetId'])
        print('Public subnet1= '+ subnet['Subnet']['SubnetId'])
        print('exiting add_subnet')
        return(subnet['Subnet']['SubnetId']) 

    def add_VPC_security_group(ec2,vpc,groupname,description,IpPermissions):
        print('entered add_VPC_security_group')
        TagEasyunSecurityGroup= [{'ResourceType':'security-group','Tags': TagEasyun}]
        
        secure_group = ec2.create_security_group(GroupName=groupname, Description=description, VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup)
        
        ec2.authorize_security_group_ingress(
            GroupId=secure_group['GroupId'],
            IpPermissions=IpPermissions)
        
        print('secure_group= '+secure_group['GroupId'])
        print('exiting add_VPC_security_group')
        return(secure_group['GroupId'])


    def add_VPC_db(vpc_id,region):
        print('entered add_VPC_db')
        #dc = Datacenter(name='Easyun',cloud='AWS', account_id='666621994060', region=region,vpc_id='vpc-00bcc6b87f368643f',create_date=datetime.utcnow())
                # print("11123")
        # print(str(datetime.utcnow())+"\n")
        # print("cccc")
        # #dc = Datacenter(id=1,name='Easyun',cloud='AWS', account_id='666621994060', region=REGION,vpc_id='vpc-00bcc6b87f368643f')
        # dc = Datacenter(id=1,name='Easyun',cloud='AWS', account_id='666621994060', region=REGION,vpc_id='vpc-00bcc6b87f368643f',create_date=datetime.utcnow())
        # # query account id from DB (only one account for both phase 1 and 2) ????
        # #new_datacenter = Datacenter(name='Easyun',cloud='AWS', account='guest-1', region=region,vpc_id=vpc.id,credate=datetime.date())
        # #dc
        # #dc.from_dict(newuser, new_user=True)
        # db.session.add(dc)
        # print("ddddd")
        # db.session.commit()
        # print("eeeee")
        # datacenter = Datacenter.query.filter(id=1).first()
        # print(datacenter)

        datacenters = Datacenter.query.all()
        print(datacenters)

        for datacenter in datacenters:
            print(datacenter)
            db.session.delete(datacenter)
            db.session.commit()


        now = datetime.utcnow()
        datacenter = Datacenter(name='Easyun',cloud='AWS', account_id='666621994060', region=region,vpc_id=vpc_id,create_date=now)
        # query account id from DB (only one account for both phase 1 and 2) ????
        #new_datacenter = Datacenter(name='Easyun',cloud='AWS', account='guest-1', region=region,vpc_id=vpc.id,credate=datetime.date())
        #dc
        #dc.from_dict(newuser, new_user=True)
        db.session.add(datacenter)
        db.session.commit()
        # datacenter = Datacenter.query.first()
        # print(datacenter)
        print('exiting add_VPC_db')
        return True

        # print(new_datacenter)
        # db.session.add(new_datacenter)
        
        # datacenter = Datacenter.query.filter(id=2).first()
        # print(datacenter)



    def view_func(request):
        # 增
        new_datacenter = Datacenter(id=1, region='test')
        db.session.add(new_datacenter)

        # 查
        datacenter = Datacenter.query.filter(id=1).first()

        # 修改
        datacenter.region = 'new_test'
        db.session.commit()
