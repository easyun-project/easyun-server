# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Bucket Management API
  @desc:    .
"""

from apiflask import APIBlueprint
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.providers import get_datacenter
from .schemas import StMsgOut, BucketBasic, BucketModel, AddBucketParm, BucketPropertyParm, BucketPublicParm, BucketIdQuery, BucketIdParm, BucketDetail, BucketPropertyOut, BucketPermissionOut


bp = APIBlueprint('Bucket', __name__, url_prefix='/bucket')
from . import api_object_mgt


@bp.get('')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(BucketModel(many=True))
def list_bkt_detail(parm):
    '''获取全部存储桶(Bucket)信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        bucketList = dc.resource.list_all_bucket()
        response = Result(detail=bucketList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(BucketBasic(many=True))
def get_bkt_list(parm):
    '''获取全部存储桶(Bucket)列表'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        bucketList = dc.resource.get_bucket_list()
        response = Result(detail=bucketList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/<bucket_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(BucketDetail)
def get_bkt_detail(bucket_id, parm):
    '''获取指定存储桶(Bucket)的详细信息'''
    dcName = parm['dc']
    try:
        bkt = dc.get_bucket(bucket_id)
        bucketDetail = bkt.get_detail()
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


@bp.post('')
@bp.auth_required(auth_token)
@bp.input(AddBucketParm, arg_name='parm')
@bp.output(BucketBasic)
def add_bucket_s3(parm):
    '''新增存储桶(S3 Bucket)'''
    dcName = parm['dcName']
    bucketId = parm['bucketId']
    bucketOptions = parm['bucketOptions']
    try:
        dc = get_datacenter(dcName)
        newBucket = dc.resource.create_bucket(bucketId, bucketOptions)
        resp = Result(
            detail={
                'bucketId': newBucket.id,
                'bucketRegion': bucketOptions['regionCode'],
                # 'createTime': newBucket.bucketObj.creation_date,
            },
            status_code=201,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=4001)
        resp.err_resp()


@bp.post('/add')
@bp.auth_required(auth_token)
@bp.input(AddBucketParm, arg_name='parm')
@bp.output(BucketBasic)
def add_bucket_cc(parm):
    '''新增存储桶(S3 Bucket)[Cloudcontrol]'''
    bucketId = parm['bucketId']
    bktRegion = parm['bktRegion']
    dcName = parm['dcName']
    try:
        dc = get_datacenter(dcName)
        result = dc.resource.create_bucket_cc(bucketId, bktRegion, parm)
        response = Result(detail=result, status_code=200)
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4001,
        )
        return response.err_resp()


@bp.delete('')
@bp.auth_required(auth_token)
@bp.input(BucketIdParm, arg_name='parm')
@bp.output(StMsgOut)
def delete_bucket(parm):
    '''删除存储桶(S3 Bucket)'''
    dcName = parm['dcName']
    bucketId = parm['bucketId']
    try:
        bkt = dc.get_bucket(bucketId)
        oprtRes = bkt.delete()
        resp = Result(detail=oprtRes, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=4003)
        resp.err_resp()


@bp.put('/<bucket_id>/property')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='query')
@bp.input(BucketPropertyParm, arg_name='parms')
@bp.output(BucketPropertyOut)
def modify_bucket_property(bucket_id, query, parms):
    '''修改存储桶(S3 Bucket)属性'''
    dcName = query.get('dc')
    isEncryption = parms.get('isEncryption')
    isVersioning = parms.get('isVersioning')
    oprtRes = {'bucketId': bucket_id}
    try:
        dc = get_datacenter(dcName)
        bkt = dc.get_bucket(bucket_id)        
        if isEncryption is not None and isEncryption is not bkt.get_bkt_encryption():
            bkt.set_default_encryption(isEncryption)
            oprtRes.update({'isEncryption': isEncryption})
        if isVersioning is not None and isVersioning is not bkt.get_bkt_versioning():
            bkt.set_bkt_versioning(isVersioning)
            oprtRes.update({'isVersioning': isVersioning})
        resp = Result(detail=oprtRes, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=4003)
        resp.err_resp()


@bp.put('/<bucket_id>/permission')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='query')
@bp.input(BucketPublicParm, arg_name='parms')
@bp.output(BucketPermissionOut)
def modify_bucket_policy(bucket_id, query, parms):
    '''修改存储桶的Public Block Policy'''
    dcName = query.get('dc')
    pubConfig = parms
    oprtRes = {'bucketId': bucket_id}
    try:
        dc = get_datacenter(dcName)
        bkt = dc.get_bucket(bucket_id)
        bkt.set_public_access(pubConfig)
        oprtRes.update({'bucketPermission': bkt.get_public_status()})
        response = Result(detail=oprtRes, status_code=200)
        return response.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=4003)
        resp.err_resp()


@bp.get('/vaildate')
@bp.auth_required(auth_token)
@bp.input(BucketIdQuery, location='query', arg_name='parms')
@bp.output(StMsgOut)
def vaildate_bkt(parms):
    '''查询存储桶名称全局范围是否可用'''
    dcName = parms['dc']
    bucketId = parms['bkt']
    try:
        dc = get_datacenter(dcName)
        if dc.validate_bucket_name(bucketId):
            isAvailable = False
        else:
            isAvailable = True
        resp = Result(detail={'isAvailable': isAvailable}, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=4004,
        )
        resp.err_resp()


# @bp.get('/pubblock')
# @auth_required(auth_token)
# @bp.input(BucketIdQuery, location='query')
# def get_bkt_public_block(parms):
#     '''获取Bucket Public Block Policy信息'''
#     dcName = parms['dc']
#     bucketId = parms['bkt']
#     try:
#         bkt = dc.get_bucket(bucketId)
#         bucketDetail = bkt.get_detail()

#         result = S3Client.get_public_access_block(Bucket=bucketId)[
#             'PublicAccessBlockConfiguration'
#         ]
#         resp = Result(detail=[{'message': result}], status_code=4013)
#         return resp.make_resp()
#     except Exception:
#         resp = Result(
#             message='Get Bucket public block policy fail',
#             status_code=4013,
#             http_status_code=400,
#         )
#         resp.err_resp()
