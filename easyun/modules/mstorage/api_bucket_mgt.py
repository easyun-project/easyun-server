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
from .schemas import AddBucketParm, BucketIdQuery, BucketIdParm, BucketPubBlockParm, BucketBasic
from . import get_st_bucket

bp = APIBlueprint('Bucket', __name__, url_prefix='/bucket')

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
