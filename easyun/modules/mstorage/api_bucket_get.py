# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Get API
  @desc:    .
  @auth:    
"""

import boto3
from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from .schemas import BucketIdQuery, BucketBasic, BucketModel, BucketDetail
from . import bp, get_st_bucket


@bp.get('/bucket')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(BucketModel(many=True))
def list_bkt_detail(parm):
    '''获取全部存储桶(Bucket)信息'''
    dcName = parm.get('dc')
    try:
        bkt = get_st_bucket(dcName)
        bucketList = bkt.list_all_bucket()

        response = Result(detail=bucketList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/bucket/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(BucketBasic(many=True))
def get_bkt_list(parm):
    '''获取全部存储桶(Bucket)列表'''
    dcName = parm.get('dc')
    try:
        bkt = get_st_bucket(dcName)
        bucketList = bkt.get_bucket_list()

        response = Result(detail=bucketList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/bucket/<bucket_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(BucketDetail)
def get_bkt_detail(bucket_id, parm):
    '''获取指定存储桶(Bucket)的详细信息【mock】'''
    dcName = parm.get('dc')
    try:
        bkt = get_st_bucket(dcName)
        bucketDetail = bkt.get_bucket_detail(bucket_id)

        response = Result(
            detail=bucketDetail,
            status_code=200,
        )
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/bucket/pubblock')
@auth_required(auth_token)
@bp.input(BucketIdQuery, location='query')
def get_bkt_public_block(parm):
    '''获取Bucket Public Block Policy信息'''
    dcName = parm.get('dc')
    bucketId = parm.get('bkt')
    S3Client = boto3.client('s3')
    try:
        result = S3Client.get_public_access_block(Bucket=bucketId)[
            'PublicAccessBlockConfiguration'
        ]
        response = Result(detail=[{'message': result}], status_code=4013)
        return response.make_resp()
    except Exception:
        response = Result(
            message='Get Bucket public block policy fail',
            status_code=4013,
            http_status_code=400,
        )
        return response.err_resp()
