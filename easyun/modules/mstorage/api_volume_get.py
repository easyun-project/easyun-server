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
from easyun.libs.utils import len_iter
from easyun.cloud.utils import query_dc_region, get_server_name
from .schemas import newVolume, VolumeDetail
from . import bp



# 定义系统盘路径
SystemDisk = ['/dev/xvda','/dev/sda1']


@bp.get('/volume')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(VolumeDetail(many=True), description='All volume list (detail)')
def list_stblock_detail(parm):
    '''获取数据中心全部块存储信息'''
    dcName=parm.get('dc')
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_ec2 = boto3.client('ec2')
        volumes = client_ec2.describe_volumes(
            Filters=[
                { 'Name': 'tag:Flag',  'Values': [dcName,] },
            ]
        )['Volumes']
        volumeList = []
        for vol in volumes:
            # nameTag = [tag['Value'] for tag in vol['Tags'] if tag.get('Key') == 'Name']
            nameTag = next((tag['Value'] for tag in vol.get('Tags') if tag["Key"] == 'Name'), None)
            attachList = []
            attachs = vol.get('Attachments')
            if attachs:
                for a in attachs:
                    # 基于卷挂载路径判断disk类型是 system 还是 user
                    diskType = 'system' if a['Device'] in SystemDisk else 'user'
                    attachList.append({
                        'attachPath' : a['Device'],
                        'attachSvrId' : a['InstanceId'],
                        'attachSvr' : get_server_name(a['InstanceId']),
                        'attachTime': a['AttachTime'],
                        'diskType': diskType,  
                    })
                    
            volItem = {
                'volumeId': vol['VolumeId'],
                'tagName': nameTag,
                'volumeState': vol['State'],
                'isEncrypted': vol['Encrypted'],
                'volumeAz': vol['AvailabilityZone'],
                'createTime': vol['CreateTime'],
                'volumeType': vol['VolumeType'],
                'volumeSize': vol['Size'],
    #             'usedSize': none,
                'volumeIops': vol.get('Iops'),
                'volumeThruput': vol.get('Throughput'),
                'volumeAttach': attachList
            }
            volumeList.append(volItem)

        resp = Result(
            detail = volumeList,
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
@bp.input(DcNameQuery, location='query')
# @bp.output(SvrListOut, description='Get Servers list')
def list_stblock_brief(parm):
    '''获取数据中心全部块存储列表[仅基础字段]'''
    dcName=parm.get('dc')
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_ec2 = boto3.client('ec2')
        volumes = client_ec2.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:Flag',
                    'Values': [dcName,]
                },
            ]
        )['Volumes']
        volumeList = []
        for vol in volumes:
            nameTag = next((tag['Value'] for tag in vol.get('Tags') if tag['Key'] == 'Name'), None)
            volItem = {
                'volumeId': vol['VolumeId'],
                'tagName': nameTag,
                'volumeType': vol['VolumeType'],
                'volumeSize': vol['Size'],
                'volumeAz': vol['AvailabilityZone'],
                'volumeState': vol['State'],
                'isAvailable': True if vol['State'] == 'available' else False
            }
            volumeList.append(volItem)

        resp = Result(
            detail = volumeList,
            status_code=200
        )
        return resp.make_resp()        

    except Exception as ex:
        resp = Result(
            detail=str(ex), 
            status_code=4103
        )
        return resp.err_resp()
