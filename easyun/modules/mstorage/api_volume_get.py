# encoding: utf-8
"""
  @module:  Block Storage Module
  @desc:    块存储(EBS) Volume 卷查询相关
  @auth:    
"""

import boto3
from flask import send_file
from flask.views import MethodView
from apiflask import auth_required, Schema, input, output
from apiflask.fields import String, Integer, Boolean
from apiflask.validators import Length
from sqlalchemy import false, true
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import len_iter, query_dc_region, query_svr_name
from . import bp, TYPE
from .schemas import newVolume


# 将磁盘管理代码从服务器模块移到存储管理模块

# 定义系统盘路径
SystemDisk = ['/dev/xvda','/dev/sda1']


@bp.get('/volume')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SvrListOut, description='Get Servers list')
def list_stblock_detail(parm):
    '''获取数据中心全部块存储信息'''
    dcName=parm.get('dc')
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_ec2 = boto3.client('ec2')
        volumeList = client_ec2.describe_volumes(
            Filters=[
                { 'Name': 'tag:Flag',  'Values': [dcName,] },
            ]
        )['Volumes']
        diskList = []
        for d in volumeList:
            # nameTag = [tag['Value'] for tag in d['Tags'] if tag.get('Key') == 'Name']
            nameTag = next((tag['Value'] for tag in d.get('Tags') if tag["Key"] == 'Name'), None)
            attach = d.get('Attachments')
            if attach:
                attachPath = attach[0].get('Device')
                insId = attach[0].get('InstanceId')
                attachSvr = query_svr_name(insId)
            else:
                attachPath = None
                attachSvr = None
            # 基于卷挂载路径判断disk类型是 system 还是 user
            diskType = 'system' if attachPath in SystemDisk else 'user'
            disk = {
                'volumeId': d['VolumeId'],
                'tagName': nameTag,
                'volumeType': d['VolumeType'],
                'volumeSize': d['Size'],
    #             'usedSize': none,
                'volumeIops': d.get('Iops'),
                'volumeThruput': d.get('Throughput'),
                'volumeState': d['State'],
                'attachSvr': attachSvr,
                'attachPath': attachPath,
                'diskType': diskType,
                'isEncrypted': d['Encrypted'],
                'volumeAz': d['AvailabilityZone'],
                'createTime': d['CreateTime'].isoformat(),
            }
            diskList.append(disk)

        resp = Result(
            detail = diskList,
            status_code=200
        )
        return resp.make_resp()        

    except Exception as ex:
        resp = Result(
            detail=str(ex), 
            status_code=4101
        )
        return resp.err_resp()



@bp.get('/volume/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SvrListOut, description='Get Servers list')
def list_stblock_brief(parm):
    '''获取数据中心全部块存储列表[仅基础字段]'''
    dcName=parm.get('dc')
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_ec2 = boto3.client('ec2')
        volumeList = client_ec2.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Flag',
                    'Values': [dcName,]
                },
            ]
        )['Volumes']
        diskList = []
        for d in volumeList:
            nameTag = next((tag['Value'] for tag in d.get('Tags') if tag['Key'] == 'Name'), None)
            disk = {
                'volumeId': d['VolumeId'],
                'tagName': nameTag,
                'volumeType': d['VolumeType'],
                'volumeSize': d['Size'],
                'volumeAz': d['AvailabilityZone'],
                'volumeState': d['State'],
                'isAvailable': True if d['State'] == 'available' else False
            }
            diskList.append(disk)

        resp = Result(
            detail = diskList,
            status_code=200
        )
        return resp.make_resp()        

    except Exception as ex:
        resp = Result(
            detail=str(ex), 
            status_code=4103
        )
        return resp.err_resp()
