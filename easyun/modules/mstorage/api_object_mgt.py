# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Data(object) Management API
  @desc:    Object data management, like ls, copy, upload, download, delete
"""

from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import get_dc_name
from easyun.cloud import get_datacenter

from .schemas import ObjectKeyQuery, BucketIdQuery, ObjectContents
from .api_bucket_mgt import bp


@bp.get('/<bucket_id>/object')
@bp.auth_required(auth_token)
@bp.output(ObjectContents(many=True))
def get_object_list(bucket_id):
    '''获取指定存储桶(Bucket)内所有对象文件列表'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        bkt = dc.get_bucket(bucket_id)
        objList = bkt.list_objects()
        response = Result(detail=objList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=4002)
        return response.err_resp()


@bp.get('/<bucket_id>/<object_key>')
@bp.auth_required(auth_token)
@bp.output(ObjectContents)
def get_object_detail(bucket_id, object_key):
    '''获取指定存储桶(Bucket)内单个对象文件信息'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        bkt = dc.get_bucket(bucket_id)
        obj = bkt.get_object(object_key)
        objDetail = obj.get_detail()
        response = Result(detail=objDetail, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=4002)
        return response.err_resp()
