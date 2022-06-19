# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Data(object) Management API
  @desc:    Object data management, like ls, copy, upload, download, delete
  @auth:
"""


import boto3
from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.cloud.utils import query_dc_region
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from .schemas import ObjectKeyQuery
from .api_bucket_mgt import bp


@bp.get('/<bkt_id>/object')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def get_object_list(bucket_id, parm):
    '''获取指定存储桶(Bucket)内所有对象的详细信息'''
    dcName = parm.get('dcName')
    try:
        dcRegion = query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name=dcRegion)

        client_s3 = boto3.client('s3')
        response = client_s3.list_objects_v2(Bucket=bucket_id)
        if 'Contents' in response:
            objectList = []
            objects = response['Contents']
            for obj in objects:
                objDict = {
                    'name': obj['Key'],
                    'size': obj['Size'],
                    'storageClass': obj['StorageClass'],
                    'lastModified': obj['LastModified'].isoformat(),
                }
                objectList.append(objDict)
        else:
            response = Result(detail='nullBucket', status_code=200)
            return response.make_resp()
        response = Result(detail=objectList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/<bucket_id>/<object_key>')
@auth_required(auth_token)
@bp.input(ObjectKeyQuery, location='query')
def get_object_detail(bucket_id, object_key, parm):
    '''获取指定存储桶(Bucket)内单个对象的详细信息'''
    dcName = parm.get('dcName')

    objectList = {
        'dc': dcName,
        'bkt': bucket_id,
        'key': object_key,
    }

    response = Result(detail=objectList, status_code=200)
    return response.make_resp()
