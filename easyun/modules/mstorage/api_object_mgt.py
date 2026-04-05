# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Data(object) Management API
  @desc:    Object data management, like ls, copy, upload, download, delete
  @auth:
"""

from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.providers.aws.resource.storage.sdk_bucket import get_st_object
from .schemas import ObjectKeyQuery, BucketIdQuery, ObjectContents
from .api_bucket_mgt import bp


@bp.get('/<bucket_id>/object')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
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
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='bucket_id')
@bp.output(ObjectContents)
def get_object_detail(bucket_id, object_key, parm):
    '''获取指定存储桶(Bucket)内单个对象文件信息'''
    dcName = parm['dc']
    try:
        obj = get_st_object(object_key, bucket_id)
        objDetail = obj.get_detail()
        response = Result(detail=objDetail, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=4002)
        return response.err_resp()
