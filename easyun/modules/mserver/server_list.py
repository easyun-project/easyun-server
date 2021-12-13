# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get info: Server list, Server detail
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.result import Result, make_resp, error_resp, bad_request
from datetime import date, datetime
from . import bp, REGION, FLAG
from flask import jsonify

class SvrListOut(Schema):
    ins_id = String()
    tag_name = Dict()
    ins_status = String()
    ins_type = String()
    vcpu = Integer()
    ram = String()
    subnet_id = String()
    ssubnet_id = String()
    key_name = String()
    category = String()


@bp.get('/list_all')
@auth_required(auth_token)
# @output(SvrListOut, description='Get Servers list')
def list_all_svrs():
    '''获取Easyun数据中心云服务器列表'''
    # 动态获取 vpc_id
    # client_ec2 = boto3.client('ec2', region_name = this_region)
    # vpcs = client_ec2.describe_vpcs(
    #     Filters=[
    #         {'Name': 'tag:Flag','Values': ['Easyun'],},
    #     ]
    # )
    # vpc_id = [vpc['VpcId'] for vpc in vpcs['Vpcs']][0] 

    try:
        # this_dc = Datacenter.query.filter_by(name='Easyun').first()
        this_dc = Datacenter.query.first()

        resource_ec2 = boto3.resource('ec2', region_name=REGION)
        vpc = resource_ec2.Vpc(this_dc.vpc_id)
        # vpc.instances.all() 返回 EC2.Instance 对象
        list_resp = []
        for s in vpc.instances.all():
            name = [tag['Value'] for tag in s.tags if tag['Key'] == 'Name'][0]
            svr = {
                'svr_id' : s.id,
                'svr_name' : name,
                'svr_state' : s.state["Name"],
                'ins_type' : s.instance_type,
                'vcpu' : s.cpu_options['CoreCount'],
                'ram' : 'N/A', # 查找中
                'ebs' : 'N/A', # 查找中
                'os' : resource_ec2.Image(s.image_id).platform_details,               
                'rg_az' : resource_ec2.Subnet(s.subnet_id).availability_zone,
                'pub_ip' : s.public_ip_address
            }
            list_resp.append(svr)

        response = Result(
            detail = list_resp,
            status_code=3001
        )

        return response.make_resp()

    except Exception:
        response = Result(
            message='list servers failed', status_code=3001,http_status_code=400
        )
        response.err_resp()