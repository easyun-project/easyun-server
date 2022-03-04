# -*- coding: utf-8 -*-
"""
  @module:  Storage Volume Detail
  @desc:    Get volume detail info
  @auth:    
"""

import boto3
from apiflask import Schema, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import query_dc_region, query_svr_name, set_boto3_region
from . import bp


# 定义系统盘路径
SystemDisk = ['/dev/xvda','/dev/sda1']


class DiskOut(Schema):
   id = String()
   state = String()
   create_time = String()
   tags = String()

@bp.get('/volume/<vol_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @bp.output(DiskOut)
def get_volume_detail(vol_id, parm):
    '''获取指定块存储(Volume)详细信息'''
    dcName=parm.get('dc')
    try:
        # 设置 boto3 接口默认 region_name
        dcRegion =  set_boto3_region(dcName)
        resource_ec2 = boto3.resource('ec2')
        thisVol = resource_ec2.Volume(vol_id)
        # nameTag = [tag['Value'] for tag in thisVol.tags if tag.get('Key') == 'Name']
        # 加一个判断，避免tags为空时报错
        if thisVol.tags:
            nameTag = next((tag['Value'] for tag in thisVol.tags if tag['Key'] == 'Name'), None)
        else:
            nameTag = None
        
        attachList = []
        attachs = thisVol.attachments
        if attachs:
            for a in attachs:
                # 基于卷挂载路径判断disk类型是 system 还是 user
                diskType = 'system' if a['Device'] in SystemDisk else 'user'
                attachList.append({
                    'attachPath' : a['Device'],
                    'attachSvr' : query_svr_name(a['InstanceId']),
                    'attachTime': a['AttachTime'].isoformat(),
                    'diskType': diskType,  
                })

        volBasic = {
            'volumeId': thisVol.volume_id,
            # 'tagName': nameTag[0] if len(nameTag) else None,
            'tagName' : nameTag,
            'volumeState': thisVol.state,
            'createTime': thisVol.create_time.isoformat(),
            # 'attachPath': attachPath,
            'volumeAz': thisVol.availability_zone,  
        }

        volConfig = {
            'volumeType': thisVol.volume_type,
            'volumeSize': thisVol.size,
#             'usedSize': none,
            'volumeIops': thisVol.iops,
            'volumeThruput': thisVol.throughput,
            'isEncrypted': thisVol.encrypted,                
        }

        volTags = [t for t in thisVol.tags if t['Key'] not in ["Flag","Name"]]

        response = Result(
            detail={
                'volumeBasic':volBasic,
                'volumeAttach':attachList,
                'volumeConfig':volConfig,
                'userTags':volTags
            },
            status_code=200
            )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=4102, 
            http_status_code=400
        )
        response.err_resp()
