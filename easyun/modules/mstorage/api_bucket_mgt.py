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
from .schemas import BucketBasic, BucketModel, AddBucketParm, BucketIdQuery, BucketIdParm, BucketPubBlockParm, BucketDetail
from . import get_st_bucket

bp = APIBlueprint('Bucket', __name__, url_prefix='/bucket')


@bp.get('')
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


@bp.get('/list')
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


@bp.get('/<bucket_id>')
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


@bp.get('/pubblock')
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


@bp.get('/vaildate')
@auth_required(auth_token)
@bp.input(BucketIdQuery, location='query')
def vaildate_bkt(parm):
    '''查询存储桶(bucket)名称是否可用'''
    dcName = parm['dc']
    bucketId = parm['bkt']
    try:
        bkt = get_st_bucket(dcName)
        isAvailable = bkt.vaildate_bucket_name(bucketId)

        resp = Result(detail={'isAvailable': isAvailable}, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=4004,
        )
        resp.err_resp()


@bp.post('')
@auth_required(auth_token)
@bp.input(AddBucketParm)
@bp.output(BucketBasic)
def add_bucket_s3(parm):
    '''新增存储桶(S3 Bucket)'''
    dcName = parm['dcName']
    bucketId = parm['bucketId']
    bucketOptions = parm['bucketCreateParm']
    try:
        bkt = get_st_bucket(dcName)
        newBucket = bkt.create_bucket(bucketId, bucketOptions)

        resp = Result(
            detail={
                'bucketId': newBucket.name,
                'bucketRegion': bucketOptions['regionCode'],
                'createTime': newBucket.creation_date,
            },
            status_code=200,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=4001,
        )
        resp.err_resp()


@bp.delete('')
@auth_required(auth_token)
@bp.input(BucketIdParm)
def delete_bucket(parm):
    '''删除存储桶(S3 Bucket)'''
    dcName = parm['dcName']
    bucketId = parm['bucketId']
    try:
        bkt = get_st_bucket(dcName)
        bkt.delete_bucket(bucketId)
        response = Result(
            detail={'bucketId': bucketId}, message='bucket delete successfully'
        )
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=4003, http_status_code=400)
        return response.err_resp()


@bp.put('/pubblock')
@auth_required(auth_token)
@bp.input(BucketPubBlockParm)
def modify_bucket_policy(parm):
    '''修改存储桶的Public Block Policy'''
    S3Client = boto3.client('s3')

    bucketId = parm['bucketId']

    newAcl = parm['newAcl']
    allAcl = parm['allAcl']
    newPolicy = parm['newPolicy']
    allPolicy = parm['allPolicy']

    try:
        result = S3Client.put_public_access_block(
            Bucket=bucketId,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': newAcl,
                'IgnorePublicAcls': allAcl,
                'BlockPublicPolicy': newPolicy,
                'RestrictPublicBuckets': allPolicy,
            },
        )['ResponseMetadata']['HTTPStatusCode']
        if result == 200:
            message = 'Modify public block policy success'
        else:
            message = 'Modify public block policy fail'
        response = Result(detail=[{'message': message}], status_code=4003)
        return response.make_resp()
    except Exception:
        response = Result(
            message='Modify public block policy fail',
            status_code=4003,
            http_status_code=400,
        )
        return response.err_resp()


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
