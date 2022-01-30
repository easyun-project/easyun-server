# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get info: Server list, Server detail
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.models import Datacenter
from easyun.common.schemas import DcNameQuery
from datetime import date, datetime
from . import bp, REGION, VPC
from flask import request, jsonify

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


@bp.get('')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SvrListOut, description='Get Servers list')
def list_server_detail(parm):
    '''获取数据中心全部云服务器信息'''
    # dcName = request.args.get('dc', 'Easyun')  #获取查询参数 ?dc=xxx ,默认值‘Easyun’
    # thisDC = Datacenter(name = dcName)
    thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
    dcRegion = thisDC.get_region()
    dcVpc = thisDC.get_vpc()

    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = dcRegion )

    try:
        resource_ec2 = boto3.resource('ec2')
        vpc = resource_ec2.Vpc(dcVpc)

        svrList = []
        # vpc.instances.all() 返回 EC2.Instance 对象
        for s in vpc.instances.all():
            #获取tag:Name
            tagName = [tag['Value'] for tag in s.tags if tag['Key'] == 'Name']
            #获取ebs卷大小并进行累加
            ebs_size = 0
            for disk in s.block_device_mappings:            
                ebs_id = disk['Ebs']['VolumeId']
                ebs_size = ebs_size + resource_ec2.Volume(ebs_id).size        
            #获取内存        
            client_ec2 = boto3.client('ec2')
            ins_type = client_ec2.describe_instance_types(InstanceTypes=[s.instance_type])
            ram_m = ins_type['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']
            svr = {
                'svrId' : s.id,
                'tagName': tagName[0] if len(tagName) else None,
                'svrState' : s.state["Name"],
                'insType' : s.instance_type,
                'vpuNumb' : s.cpu_options['CoreCount'],
                'ramSize' : ram_m/1024,
                'ebsSize' : ebs_size, 
                'osName' : resource_ec2.Image(s.image_id).platform_details,               
                'azName' : resource_ec2.Subnet(s.subnet_id).availability_zone,
                'pubIp' : s.public_ip_address
            }
            svrList.append(svr)

        resp = Result(
            detail = svrList,
            status_code=200
        )
        return resp.make_resp()

    except Exception:
        resp = Result(
            message='list servers failed', 
            status_code=3001,
            http_status_code=400
        )
        return resp.err_resp()



# @bp.get('/<svr_id>')
# def get_server_detail(svr_id):
#     '''获取指定云服务器详情'''
    # 由于服务器详情页面有一个获取全部信息的api，此处略
    # 整合到 api/server/detail


@bp.get('/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SvrListOut, description='Get Servers list')
def list_server_brief(parm):
    '''获取数据中心全部云服务器列表[仅基础字段]'''
    # dcName = request.args.get('dc', 'Easyun')  #获取查询参数 ?dc=xxx ,默认值‘Easyun’
    # thisDC = Datacenter(name = dcName)
    thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
    dcRegion = thisDC.get_region()
    dcVpc = thisDC.get_vpc()

    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = dcRegion )

    try:
        resource_ec2 = boto3.resource('ec2')
        vpc = resource_ec2.Vpc(dcVpc)

        svrList = []
        # vpc.instances.all() 返回 EC2.Instance 对象
        for s in vpc.instances.all():
            #获取tag:Name
            tagName = [tag['Value'] for tag in s.tags if tag['Key'] == 'Name']
            svr = {
                'svrId' : s.id,
                'tagName': tagName[0] if len(tagName) else None,
                'svrState' : s.state["Name"],
                'insType' : s.instance_type,          
                'azName' : resource_ec2.Subnet(s.subnet_id).availability_zone,
            }
            svrList.append(svr)

        resp = Result(
            detail = svrList,
            status_code=200
        )
        return resp.make_resp()

    except Exception:
        resp = Result(
            message='list servers failed', 
            status_code=3001,
            http_status_code=400
        )
        return resp.err_resp()