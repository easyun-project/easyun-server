# -*- coding: utf-8 -*-
"""
  @module:  Object Storage Get API
  @desc:    .
  @auth:    
"""

from email import message
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.schemas import EmptySchema 
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result, make_resp, error_resp, bad_request
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