# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Bucket Management API
  @desc:    .
  @auth:
"""

import boto3
from apiflask import APIBlueprint, auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.cloud.aws import get_datacenter
from easyun.cloud.aws.workload import get_st_bucket
from easyun.cloud.aws.workload.sdk_bucket import vaildate_bucket_exist
from .schemas import BucketBasic, BucketModel, AddBucketParm, BucketPropertyParm, BucketPublicParm, BucketIdQuery, BucketIdParm, BucketDetail


bp = APIBlueprint('Bucket', __name__, url_prefix='/bucket')
from . import api_object_mgt


@bp.get('')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(BucketModel(many=True))
def list_bkt_detail(parm):
    '''获取全部存储桶(Bucket)信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        bucketList = dc.workload.list_all_bucket()
        response = Result(detail=bucketList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(BucketBasic(many=True))
def get_bkt_list(parm):
    '''获取全部存储桶(Bucket)列表'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        bucketList = dc.workload.get_bucket_list()
        response = Result(detail=bucketList, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/<bucket_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(BucketDetail)
def get_bkt_detail(bucket_id, parm):
    '''获取指定存储桶(Bucket)的详细信息'''
    dcName = parm['dc']
    try:
        bkt = get_st_bucket(bucket_id, dcName)
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
@auth_required(auth_token)
@bp.input(AddBucketParm)
@bp.output(BucketBasic)
def add_bucket_s3(parm):
    '''新增存储桶(S3 Bucket)'''
    dcName = parm['dcName']
    bucketId = parm['bucketId']
    bucketOptions = parm['bucketOptions']
    try:
        dc = get_datacenter(dcName)
        newBucket = dc.workload.create_bucket(bucketId, bucketOptions)
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
@auth_required(auth_token)
@bp.input(AddBucketParm)
def add_bucket_cc(parm):
    '''新增存储桶(S3 Bucket)[Cloudcontrol]'''
    bucketId = parm['bucketId']
    bktRegion = parm['bktRegion']
    dcName = parm['dcName']
    flagTag = {'Key': 'Flag', 'Value': dcName}

    desiredState = {
        'bucketId': bucketId,
        'VersioningConfiguration': {
            'Status': 'Enabled' if parm['isVersioning'] else 'Suspended'
        },
        'PublicAccessBlockConfiguration': {
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True,
        },
        'Tags': [flagTag],
    }
    if parm['isEncryption']:
        desiredState.update(
            {
                'BucketEncryption': {
                    'ServerSideEncryptionConfiguration': [
                        {
                            'BucketKeyEnabled': parm['isEncryption'],
                            'ServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'},
                        }
                    ]
                }
            }
        )
    try:
        # 调cloudtontro接口创建bucket
        client_cc = boto3.client('cloudcontrol', region_name=bktRegion)
        bucket = client_cc.create_resource(
            TypeName='AWS::S3::Bucket', DesiredState=str(desiredState)
        )
        response = Result(
            detail=bucket['ProgressEvent'],
            # detail = {'bucketId' : bucket['ProgressEvent']['Identifier']},
            status_code=200,
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4001,
        )
        return response.err_resp()


@bp.delete('')
@auth_required(auth_token)
@bp.input(BucketIdParm)
def delete_bucket(parm):
    '''删除存储桶(S3 Bucket)'''
    dcName = parm['dcName']
    bucketId = parm['bucketId']
    try:
        bkt = get_st_bucket(bucketId, dcName)
        oprtRes = bkt.delete()
        resp = Result(detail=oprtRes, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=4003)
        resp.err_resp()


@bp.put('/<bucket_id>/property')
@auth_required(auth_token)
@bp.input(BucketPropertyParm)
def modify_bucket_property(bucket_id, parms):
    '''修改存储桶(S3 Bucket)属性'''
    isEncryption = parms.get('isEncryption')
    isVersioning = parms.get('isVersioning')
    oprtRes = {'bucketId': bucket_id}
    try:
        bkt = get_st_bucket(bucket_id)        
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
@auth_required(auth_token)
@bp.input(BucketPublicParm)
def modify_bucket_policy(bucket_id, parms):
    '''修改存储桶的Public Block Policy'''
    pubConfig = parms
    oprtRes = {'bucketId': bucket_id}
    try:
        bkt = get_st_bucket(bucket_id)
        bkt.set_public_access(pubConfig)
        oprtRes.update({'bucketPermission': bkt.get_public_status()})
        response = Result(detail=oprtRes, status_code=200)
        return response.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=4003)
        resp.err_resp()


@bp.get('/vaildate')
@auth_required(auth_token)
@bp.input(BucketIdQuery, location='query')
def vaildate_bkt(parms):
    '''查询存储桶名称全局范围是否可用【fix-me】'''
    dcName = parms['dc']
    bucketId = parms['bkt']
    try:
        if vaildate_bucket_exist(bucketId, dcName):
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
#         bkt = get_st_bucket(bucketId, dcName)
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
