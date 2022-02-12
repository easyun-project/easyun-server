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
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.models import Datacenter
from easyun.common.schemas import DcNameQuery
# from easyun.common.utils import query_svr_name
from datetime import date, datetime
from . import bp
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
    dcName = parm['dc']
    thisDC = Datacenter.query.filter_by(name = dcName).first()
    dcRegion = thisDC.get_region()

    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = dcRegion )

    try:
        # vpc = resource_ec2.Vpc(dcVPC)
        client_ec2 = boto3.client('ec2')

        # 通过 ec2.instances.filter() 接口获取 instance 对象列表
        resource_ec2 = boto3.resource('ec2')       
        svrIterator = resource_ec2.instances.filter(
            Filters=[
                {'Name': 'tag:Flag', 'Values': [dcName]},
            ],
        )        
        svrList = []
        
        for s in svrIterator:
            #获取tag:Name
            # nameTag = [tag['Value'] for tag in s.tags if tag['Key'] == 'Name']
            nameTag = next((tag['Value'] for tag in s.tags if tag["Key"] == 'Name'), None)
            #获取ebs卷总容量
            diskSize = 0
            for disk in s.block_device_mappings:            
                ebsId = disk['Ebs']['VolumeId']
                diskSize += resource_ec2.Volume(ebsId).size        
            #获取内存容量            
            insType = client_ec2.describe_instance_types(InstanceTypes=[s.instance_type])
            ramSize = insType['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']
            svrItem = {
                'svrId' : s.id,
                'tagName': nameTag,
                'svrState' : s.state["Name"],
                'insType' : s.instance_type,
                'vpuNum' : s.cpu_options['CoreCount'],
                'ramSize' : ramSize/1024,
                'diskSize' : diskSize, 
                'osName' : resource_ec2.Image(s.image_id).platform_details,             
                # 'azName' : resource_ec2.Subnet(s.subnet_id).availability_zone,
                'azName' : s.placement.get('AvailabilityZone'),
                'pubIp' : s.public_ip_address,
                'priIp' : s.private_ip_address
            }
            svrList.append(svrItem)

        resp = Result(
            detail = svrList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message = ex, 
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
    dcName = parm['dc']
    thisDC = Datacenter.query.filter_by(name = dcName).first()
    dcRegion = thisDC.get_region()
    dcVPC = thisDC.get_vpc()

    try:
        # 通过 ec2.instances.filter() 接口获取 instance 对象列表
        resource_ec2 = boto3.resource('ec2')       
        svrIterator = resource_ec2.instances.filter(
            Filters=[
                {'Name': 'tag:Flag', 'Values': [dcName]},
            ],
        )
        svrList = []

        for s in svrIterator:
            #获取tag:Name
            nameTag = next((tag['Value'] for tag in s.tags if tag["Key"] == 'Name'), None)
            svr = {
                'svrId' : s.id,
                'tagName': nameTag,
                'svrState' : s.state["Name"],
                'insType' : s.instance_type,    
                # 'azName' : resource_ec2.Subnet(s.subnet_id).availability_zone,
                'azName' : s.placement.get('AvailabilityZone'),
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