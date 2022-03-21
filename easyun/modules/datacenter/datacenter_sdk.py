# -*- coding: utf-8 -*-
"""
  @file:    datacenter_sdk.py
  @desc:    DataCenter SDK module
"""

from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import current_app,jsonify
from datetime import date, datetime
from easyun.common.auth import auth_token
from easyun.common.models import Account,Datacenter
from easyun.common.result import Result
from easyun import db, FLAG
import boto3
import os, time
import json
import logging
from . import DC_NAME,TagEasyun,DryRun

def app_log(name):
    def wrapper1(func):
        def sub_wrapper1(*args,**kwargs):
            # print("entering into===>",func.__name__,name)
            current_app.logger.info("entering===>"+func.__name__)
            res = func(*args,**kwargs)
            current_app.logger.info("exit from===>"+func.__name__)
            return res
        return sub_wrapper1    
    return wrapper1

class datacentersdk():

    @staticmethod
    @app_log("add_subnet")
    def add_subnet(ec2,vpc,route_table,subnetName):

        TagEasyunSubnet= [ 
            {'ResourceType':'subnet', 
              "Tags": [
                {"Key": "Flag", "Value": "Easyun"},
                {"Key": "Name", "Value": subnetName[0]['name']}
               ]
            }
        ]

        try:
            subnetID = ec2.create_subnet(CidrBlock=subnetName[0]["cidr"], VpcId=vpc.id,TagSpecifications=TagEasyunSubnet,DryRun=DryRun)
            # associate the route table with the subnet
            route_table.associate_with_subnet(SubnetId=subnetID['Subnet']['SubnetId'],DryRun=DryRun)
            current_app.logger.info('Public subnet1= '+ subnetID['Subnet']['SubnetId'])
            return(subnetID['Subnet']['SubnetId']) 
        except Exception as e:
            response = Result(message='create_subnet failed', status_code=2002,http_status_code=400)
            current_app.logger.error(e)
            response.err_resp() 

    
    @staticmethod
    @app_log("add_VPC_security_group")
    def add_VPC_security_group(ec2,vpc,securitygroup):

        TagEasyunSecurityGroup= [ 
            {'ResourceType':'security-group', 
              "Tags": [
                {"Key": "Flag", "Value": "Easyun"},
                {"Key": "Name", "Value": securitygroup['name']}
               ]
            }
        ]
        
        IpPermissions=[]
        if securitygroup["enableRDP"] == "true":
           IpPermissions.append({
                'IpProtocol': 'tcp',
                'FromPort': 3389,
                'ToPort': 3389,
                'IpRanges': [{
                    'CidrIp': '0.0.0.0/0'
                }]
            })

        if securitygroup["enableSSH"] == "true":
           IpPermissions.append({
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{
                    'CidrIp': '0.0.0.0/0'
                }]
            })
            
        if securitygroup["enablePing"] == "true":
           IpPermissions.append({
                'IpProtocol': 'icmp',
                'FromPort': -1,
                'ToPort': -1,
                'IpRanges': [{
                    'CidrIp': '0.0.0.0/0'
                }]
            })
        
        try:
            secure_group_res = ec2.create_security_group(GroupName=securitygroup['name'], Description=securitygroup['name'], VpcId=vpc.id,TagSpecifications=TagEasyunSecurityGroup,DryRun=DryRun)
            
            ec2.authorize_security_group_ingress(GroupId=secure_group_res['GroupId'],IpPermissions=IpPermissions,DryRun=DryRun)
            
            current_app.logger.info('secure_group= '+secure_group_res['GroupId'])

            return(secure_group_res['GroupId'])
        except Exception:
            response = Result(message='create_security_group failed', status_code=2002,http_status_code=400)
            current_app.logger.error('create_security_group failed')
            response.err_resp() 

    @staticmethod
    @app_log("add_VPC_db")
    def add_VPC_db(vpc_id,region):
        #dc = Datacenter(name='Easyun',cloud='AWS', account_id='666621994060', region=region,vpc_id='vpc-00bcc6b87f368643f',create_date=datetime.utcnow())
        # query account id from DB (only one account for both phase 1 and 2) ????
        # datacenter = Datacenter.query.filter(id=1).first()

        datacenters = Datacenter.query.all()

        for datacenter in datacenters:
            db.session.delete(datacenter)
            db.session.commit()


        now = datetime.utcnow()

        account:Account = Account.query.get(1)
        # account:Account = Account.query.filter_by(id=1).first()
        if (account is None):
            response = Result(detail ={'Result' : 'Errors'}, message='No Account available, kindly create it first!', status_code=3001,http_status_code=400)
            response.err_resp() 
        else:
            account_id=account.account_id
            region=account.deploy_region
            datacenter = Datacenter(name='Easyun',cloud='AWS', account_id=account_id, region=region,vpc_id=vpc_id,create_date=now)
            # query account id from DB (only one account for both phase 1 and 2) ????
            #new_datacenter = Datacenter(name='Easyun',cloud='AWS', account='guest-1', region=region,vpc_id=vpc.id,credate=datetime.date())
            db.session.add(datacenter)
            db.session.commit()
            # datacenter = Datacenter.query.first()

            return True


    @staticmethod
    @app_log("list_Subnets")
    def list_Subnets(ec2,vpc_id):
        subnet_list = ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id', 'Values': [vpc_id]
                },
                {
                    'Name': 'state', 'Values': ['available']
                },
                {
                    'Name': 'tag:Flag', 'Values': [FLAG]
                },             
            ],
        )
        response = []    
        #????? why unorder or messup using this...
        # subnet_ids = [ { subnet['SubnetId'], subnet['CidrBlock'],subnet['AvailableIpAddressCount'] } for subnet in subnet_list['Subnets'] ]
        # response.append(subnet_ids)

        for subnet in subnet_list['Subnets']:
            subnet_id =  subnet['SubnetId']
            subnet_cidr =  subnet['CidrBlock']
            subnet_ipcount = subnet['AvailableIpAddressCount']
            subnet_record = {'SubnetId': subnet_id,
                    'CidrBlock': subnet_cidr,
                    'AvailableIpAddressCount': subnet_ipcount
            }
            response.append(subnet_record)
        
        current_app.logger.info(response)
        return response

    @staticmethod
    @app_log("list_keypairs")
    def list_keypairs(ec2,vpc_id):
        keypair_list = ec2.describe_key_pairs(Filters=[{'Name': 'tag:Flag', 'Values': [FLAG]}])
        # keyname_list =[ keyname['KeyName'] for keyname in keypair_list['KeyPairs']]

        # key = ec2.describe_key_pairs(Filters= [{ 'Name': 'tag:Flag', 'Values': ['Easyun']}])

        keyname_list =[ {'filename': keyname['KeyName']+'.pem'} for keyname in keypair_list['KeyPairs']]


        response = []    

        # kp_record={'Keypair filename',keypair_filename}
        response.append(keyname_list)
        
        current_app.logger.info(keyname_list)
        return response

    @staticmethod
    @app_log("list_securitygroup")
    def list_securitygroup(ec2,vpc_id):
        sg_list = ec2.describe_security_groups(
            Filters=[
                {
                    'Name': 'vpc-id', 'Values': [vpc_id]
                },
                {
                    'Name': 'tag:Flag', 'Values': [FLAG]
                },             
            ],
        )
        response = []    

        for sg in sg_list['SecurityGroups']:
            sg_GroupName =  sg['GroupName']
            sg_IpPermissions =  sg['IpPermissions']
            sg_GroupId = sg['GroupId']
            sg_record = {'GroupID': sg_GroupId,
                    'GroupName': sg_GroupName,
                    # 'IpPermissions': sg_IpPermissions
            }
            response.append(sg_record)

        current_app.logger.info(response)
        return response
