# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Data(object) Management API
  @desc:    Object data management, like ls, copy, upload, download, delete
  @auth:
"""


import boto3
from apiflask import APIBlueprint, auth_required
from easyun.common.auth import auth_token
from easyun.cloud.utils import query_dc_region
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.cloud.aws.workload import get_st_bucket, get_st_object
from .schemas import ObjectKeyQuery, BucketIdQuery, ObjectContents
from .api_bucket_mgt import bp


@bp.get('/<bucket_id>/object')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(ObjectContents(many=True))
def get_object_list(bucket_id, parm):
    '''获取指定存储桶(Bucket)内所有对象文件列表'''
    dcName = parm['dc']
    try:
        bkt = get_st_bucket(bucket_id, dcName)
        objList = bkt.list_objects()
        response = Result(
            detail=objList,
            status_code=200,
        )
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/<bucket_id>/<object_key>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def get_object_detail(bucket_id, object_key, parm):
    '''获取指定存储桶(Bucket)内单个对象文件信息【to-be-done】'''
    dcName = parm['dc']
    try:
        bkt = get_st_bucket(bucket_id, dcName)
        object = get_st_object(object_key, bucket_id)
        objectList = {
            "key": "demo_file_name.jpg",
            "modifiedTime": "2022-03-02T07:03:04+00:00",
            "size": 966569,
            "storageClass": "INTELLIGENT_TIERING",
            "type": "Image File",
            "eTag": "ccd1edb2ebf7548d8478c7a4dcd7e9a8",
        }

        response = Result(detail=objectList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()
