# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Get API
  @desc:    .
  @auth:    
"""

import boto3
from datetime import datetime, timedelta
from apiflask import Schema, input, output, auth_required
from apiflask.schemas import EmptySchema 
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result
from easyun.common.utils import len_iter, query_dc_region
from easyun.common.schemas import DcNameQuery
from .schemas import BktNameQuery
from . import bp



@bp.get('/bucket')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_bkt_detail(parm):
    '''获取全部存储桶(Bucket)信息'''
    dcName=parm.get('dc')
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_s3 = boto3.client('s3') 
        buckets = client_s3.list_buckets()['Buckets']

        bktList = []
        for bkt in buckets:
            bktName = bkt['Name']
            flagTag = query_bkt_flag(bktName)
            if flagTag == dcName:
                bktItem = {
                    'bktName' : bktName,
                    'stType' : 'storage bucket',
                    'bktRegion' : query_bkt_region(bktName),
                    # 'bktSize' : query_bkt_size(bktName),
                    # 'pubStatus' : 'private',
                    # 'statusMsg' : 'All objects are private',
                }
                bktItem.update(query_bkt_public(bktName))
                bktList.append(bktItem)
            
        response = Result(
            detail= bktList,
            status_code=200
        )
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4002,
        )
        return response.err_resp()


@bp.get('/bucket/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_bkt_brief(parm):
    '''获取全部存储桶(Bucket)列表'''
    dcName=parm.get('dc')
    try:
        dcRegion =  query_dc_region(dcName)
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_s3 = boto3.client('s3') 
        buckets = client_s3.list_buckets()['Buckets']

        bktList = []
        for bkt in buckets:
            bktName = bkt['Name']
            flagTag = query_bkt_flag(bktName)
            if flagTag == dcName:
                bktItem = {
                    'bktName' : bktName,
                    'bktRegion' : query_bkt_region(bktName)
                }
                bktList.append(bktItem)

        response = Result(
            detail= bktList,
            status_code=200
        )
        return response.make_resp()
    except Exception as ex:
        response = Result(
            message=str(ex),
            status_code=4003
        )
        return response.err_resp()


def query_bkt_flag(bktName):
    '''查询存储桶(bucket)的Tag:Flag'''
    try:
        client_s3 = boto3.client('s3')
        bktTags = client_s3.get_bucket_tagging(
            Bucket = bktName
        ).get('TagSet')
        flagTag = next((tag['Value'] for tag in bktTags if tag["Key"] == 'Flag'), None)
        return flagTag
    except Exception as ex:
        return None



def query_bkt_region(bktName):
    '''查询存储桶(bucket)所处Region'''
    client_s3 = boto3.client('s3')
    resp = client_s3.get_bucket_location(
        Bucket = bktName
    )
    bktRegion = resp.get('LocationConstraint')
    # Buckets in Region us-east-1 have a LocationConstraint of null.
    if not bktRegion:
        bktRegion = 'east-us-1'
    return bktRegion


def query_bkt_size(bktName):
    '''查询存储桶(bucket)总容量'''
    client_cw = boto3.client('cloudwatch')
    nowDtime = datetime.now()

    bktMetric = client_cw.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='BucketSizeBytes',
        Dimensions=[
            {'Name': 'BucketName','Value': bktName},
            {'Name': 'StorageType','Value': 'StandardStorage'},        
        ],
    #   Statistics=['SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum',]
        Statistics=['Average'],
        EndTime= nowDtime,        
        StartTime= nowDtime + timedelta(hours=-36),
        Period=86400,    #one day(24h)
    #     Unit='Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'None'
    ).get('Datapoints')
    metricItem = bktMetric.pop()
    if metricItem:
        bktSize = {
            'value':metricItem['Average'],
            'unit':metricItem['Unit']    
        }
        return bktSize
    else:
        raise


def query_bkt_public(bktName):
    '''查询存储桶(bucket)公开状态'''
    priMsg = 'All objects are private'
    pubMsg = 'Public'
    otherMsg = 'Objects can be public'    
    try:
        #获取当前Account ID
        thisAccount = Account.query.first()
        #step1: 判断Account Public Access Status
        client_s3ctr = boto3.client('s3control')
        acnpubConfig = client_s3ctr.get_public_access_block(
            AccountId = thisAccount.account_id
        ).get('PublicAccessBlockConfiguration')
        acnpubStatus = check_bkt_public(acnpubConfig)
        if acnpubStatus == 'private':
            return {
                'pubStatus': acnpubStatus,
                'statusMsg': priMsg
            }
        elif acnpubStatus == 'public':
        #step2: 判断Bucket Public Access Status
            client_s3 = boto3.client('s3')
            bktpubConfig = client_s3.get_public_access_block(
                Bucket=bktName
            ).get('PublicAccessBlockConfiguration')
            bktpubStatus = check_bkt_public(bktpubConfig)
            if bktpubStatus == 'public':
                pubStatus = {
                    'pubStatus': bktpubStatus,
                    'statusMsg': pubMsg
                }
            elif bktpubStatus == 'private':
                pubStatus = {
                    'pubStatus': bktpubStatus,
                    'statusMsg': priMsg
                }
            else:
                pubStatus = {
                    'pubStatus': bktpubStatus,
                    'statusMsg': otherMsg
                }
        return pubStatus

    except Exception as ex:
        return {
            'error':str(ex)
        }

def check_bkt_public(config):
    '''检查PublicAccessBlock配置对应公开状态'''
    if config:
        if config.get('IgnorePublicAcls'):
            accessStatus = 'private'
        elif not config.get('IgnorePublicAcls'):
            accessStatus = 'public'
        else: 
            accessStatus = 'other'
    else:
        accessStatus = 'other'
    return accessStatus


class bktPubBlock(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 60),
        example='easyun-bkt-test'
    )

@bp.get('/bucket/pubblock')
@auth_required(auth_token)
@input(bktPubBlock)
def get_bkt_public_block(bktPubBlock):
    '''获取Bucket Public Block Policy信息'''
    S3Client = boto3.client('s3')
    try:
        result = S3Client.get_public_access_block(
            Bucket = bktPubBlock['bucketName']
        )['PublicAccessBlockConfiguration']
        response = Result(
            detail=[{
                'message' : result
            }],
            status_code=4013
        )
        return response.make_resp()
    except Exception:
        response = Result(
            message='Get Bucket public block policy fail', status_code=4013,http_status_code=400
        )
        return response.err_resp()