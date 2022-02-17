# -*- coding: utf-8 -*-
"""
  @module:  Storage Volume Detail
  @desc:    Get volume detail info
  @auth:    
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import query_dc_region, query_svr_name
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
@input(DcNameQuery, location='query')
# @output(DiskOut)
def get_server_detail(vol_id, parm):
    '''获取指定块存储(Volume)详细信息'''
    dcName=parm.get('dc')
    try:
        dcRegion =  query_dc_region(dcName)
        resource_ec2 = boto3.resource('ec2', region_name=dcRegion)
        thisDisk = resource_ec2.Volume(vol_id)
        # nameTag = [tag['Value'] for tag in thisDisk.tags if tag.get('Key') == 'Name']
        nameTag = next((tag['Value'] for tag in thisDisk.tags if tag['Key'] == 'Name'), None)
        attach = thisDisk.attachments
        if attach:
            attachPath = attach[0].get('Device')
            insId = attach[0].get('InstanceId')
            attachSvr = query_svr_name(insId)
        else:
            attachPath = None
            attachSvr = None
        
        diskType = 'system' if attachPath in SystemDisk else 'user'

        volBasic = {
                'volumeId': thisDisk.volume_id,
                # 'tagName': nameTag[0] if len(nameTag) else None,
                'tagName' : nameTag,
                'volumeState': thisDisk.state,
                'createTime': thisDisk.create_time.isoformat(),
                'attachPath': attachPath,
                'volumeAz': thisDisk.availability_zone,  
        }
        volAttach = {
                'attachSvr': attachSvr,
                'attachPath': attachPath,
                'diskType': diskType,              
        }
        volConfig = {
                'volumeType': thisDisk.volume_type,
                'volumeSize': thisDisk.size,
    #             'usedSize': none,
                'volumeIops': thisDisk.iops,
                'volumeThruput': thisDisk.throughput,
                'isEncrypted': thisDisk.encrypted,                
        }

        response = Result(
            detail={
                'volBasic':volBasic,
                'volAttach':volAttach,
                'volConfig':volConfig,
                'volTags':[
                    {'Key':'Env', 'Value':'development'}
                ]
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