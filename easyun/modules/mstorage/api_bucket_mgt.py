# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Bucket Management API
  @desc:    .
  @auth:    
"""  

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.schemas import EmptySchema 
from apiflask.fields import Integer, String, List, Dict, Boolean
from apiflask.validators import Length, OneOf
from flask import jsonify
from sqlalchemy import true
from werkzeug.wrappers import response
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from .schemas import BktNameQuery
from . import bp



class newBucket(Schema):
    bktName = String(
        required=True, 
        validate=Length(0, 60),
        example='easyun-bkt-test'
    )
    dcName = String(
        required=True,
        example='Easyun'
    )
    bktRegion = String(
        required=True,
        example='us-east-1'
    )
    isVersioning = Boolean(
        required=True,
        example=False)
    isEncryption = Boolean(
        required=True,
        example=False)

    
# 新增bucket
@bp.post('/bucket')
@auth_required(auth_token)
@input(newBucket)
def add_bucket_cc(parm):
    '''新增存储桶(S3 Bucket)[Cloudcontrol]'''
    bktName = parm['bktName']
    bktRegion = parm['bktRegion']
    dcName=parm['dcName']
    flagTag = {'Key':'Flag','Value':dcName}

    desiredState = {
        'BucketName' : bktName,
        'VersioningConfiguration' : {
            'Status': 'Enabled' if parm['isVersioning'] else 'Suspended'
        },
        'PublicAccessBlockConfiguration' : {
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
        'Tags' : [flagTag],
    }

    if parm['isEncryption']:
        desiredState.update(
            {'BucketEncryption' : {
                'ServerSideEncryptionConfiguration':[{
                    'BucketKeyEnabled' : parm['isEncryption'] ,
                    'ServerSideEncryptionByDefault' : {'SSEAlgorithm' : 'AES256'}}
                ]
            }}
        )

    try:
        #调cloudtontro接口创建bucket
        client_cc = boto3.client('cloudcontrol', region_name=bktRegion)
        bucket = client_cc.create_resource(
            TypeName = 'AWS::S3::Bucket',
            DesiredState = str(desiredState)
        )
        
        response = Result(
            detail = bucket['ProgressEvent'],
            # detail = {'bucketName' : bucket['ProgressEvent']['Identifier']},
            status_code=200
        )
        return response.make_resp()
        
    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=4001,
        )
        return response.err_resp()


@bp.post('/bucket2')
@auth_required(auth_token)
@input(newBucket)
def add_bucket_s3(parm):
    '''新增存储桶(S3 Bucket)'''
    bktName = parm['bktName']
    bktRegion = parm['bktRegion']
    dcName=parm['dcName']
    flagTag = {'Key':'Flag','Value':dcName}

    try:
        client_s3 = boto3.client('s3', region_name=bktRegion)
        #step1: 新建Bucket 
        bucket = client_s3.create_bucket(
            # ACL='private'|'public-read'|'public-read-write'|'authenticated-read',
            Bucket=bktName,
            CreateBucketConfiguration={
                'LocationConstraint': bktRegion
            },
            # GrantFullControl='string',
            # GrantRead='string',
            # GrantReadACP='string',
            # GrantWrite='string',
            # GrantWriteACP='string',
            # ObjectLockEnabledForBucket=True|False,
            # ObjectOwnership='BucketOwnerPreferred'|'ObjectWriter'|'BucketOwnerEnforced'
        )
        bucket.wait_until_exists(
    ExpectedBucketOwner='string'
)

        #step2: 设置Bucket encryption，默认不启用


        #step3: 设置Bucket encryption，默认不启用

        #step4: 设置Bucket Tag:Flag 标签
        
        #step5:  设置Bucket public access默认private
        set_defalt_pub_access = client_s3.put_public_access_block(
            Bucket=bktName,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )        
        
        response = Result(
            detail = bucket,
            # detail = {'bucketName' : bucket['ProgressEvent']['Identifier']},
            status_code=200
        )
        return response.make_resp()
        
    except Exception as ex:
        response = Result(
            message=str(ex), 
            status_code=4001,
        )
        return response.err_resp()


@bp.get('/object/vaildate')
@auth_required(auth_token)
@input(BktNameQuery, location='query')
def vaildate_bkt(parm):
    '''查询存储桶(bucket)名称是否可用'''
    try:
        resource_s3 = boto3.resource('s3') 
        bucket = resource_s3.Bucket(parm['bktName'])

        if bucket.creation_date:
            result = {
               'isAvailable' : False
            }
        else:
            result = {
               'isAvailable' : True
            }

        response = Result(
            detail=result,
            status_code=200
        )
        return response.make_resp()
    except Exception as ex:
        response = Result(
            # message='Get bucket message failed', 
            message=str(ex),
            status_code=4004,
        )
        return response.err_resp()


class deleteBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )


@bp.delete('/bucket')
@auth_required(auth_token)
@input(deleteBucket)
def delete_bucket(deleteBucket):
    '''删除存储桶(S3 Bucket)'''
    bucketName = deleteBucket['bucketName']
    CLIENT = boto3.client('s3')
    try:
        result = CLIENT.delete_bucket(
            Bucket = bucketName
        )
        response = Result(
            detail=[{
                'message' : 'bucket delete succee'
            }],
            status_code=4003
        )
        return response.make_resp()
    except Exception:
        response = Result(
            message='bucket delete failed', status_code=4003,http_status_code=400
        )
        return response.err_resp()
        