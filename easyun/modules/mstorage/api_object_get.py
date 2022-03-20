# -*- coding: utf-8 -*-
"""
  @module:  Storage Object Detail
  @desc:    Get object detail info
  @auth:    
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.utils import len_iter, query_dc_region
from easyun.common.result import Result, make_resp, error_resp, bad_request
from .schemas import ObjectListQuery,ObjectQuery
from . import bp

@bp.get('/bucket/object/list')
@auth_required(auth_token)
@input(ObjectListQuery, location='query')
def get_object_list(parm):
    '''获取指定存储桶(Bucket)内对象列表的详细信息'''
    dcName=parm.get('dcName')
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_s3 = boto3.client('s3') 
        response = client_s3.list_objects_v2(Bucket=parm.get('bktName'))
        if 'Contents' in response :
            objectList = []
            objects = response['Contents']
            for obj in objects:
                objDict = {
                    'name' : obj['Key'],
                    'size' : obj['Size'],
                    'storageClass' : obj['StorageClass'],
                    'lastModified' : obj['LastModified'].isoformat()
                }
                objectList.append(objDict)
        else :
            response = Result(
                detail= 'nullBucket',
                status_code=200
            )
            return response.make_resp()
        response = Result(
            detail= objectList,
            status_code=200
        )
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()

@bp.get('/bucket/object')
@auth_required(auth_token)
@input(ObjectQuery, location='query')
def get_object_detail(parm):
    '''获取指定存储桶(Bucket)内单个对象的详细信息'''
    dcName=parm.get('dcName')
    pass