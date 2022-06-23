# -*- coding: utf-8 -*-
"""
  @module:  Bucket (S3) SDK Module
  @desc:    AWS SDK Boto3 EC2 Client and Resource Wrapper. 
  @auth:
"""

import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from easyun.libs.utils import len_iter
from easyun.common.models import Account
from ...utils import get_easyun_session


def query_bucket_flag(bucket):
    '''查询存储桶(bucket)的Tag:Flag'''
    try:
        bktTags = bucket.Tagging().tag_set
        flagTag = next((tag['Value'] for tag in bktTags if tag["Key"] == 'Flag'), None)
        return flagTag
    except ClientError:
        return None


def check_bucket_public(block_config):
    '''检查PublicAccessBlock配置对应公开状态'''
    if block_config:
        if block_config.get('IgnorePublicAcls'):
            accessStatus = 'private'
        elif not block_config.get('IgnorePublicAcls'):
            accessStatus = 'public'
        else:
            accessStatus = 'other'
    else:
        accessStatus = 'other'
    return accessStatus


def vaildate_bucket_exist(bucket_id, dc_name=None):
    '''检查bucket是否存在'''
    session = get_easyun_session(dc_name)
    bucket = session.resource('s3').Bucket(bucket_id)
    isExist = True if bucket.creation_date else False
    return isExist


def get_file_type(object_key):
    '''根据文件名(object key)后缀获取文件类型'''
    if object_key[-1] == '/':
        return 'Folder'
    else:
        suffix = os.path.splitext(object_key)[-1][1:].lower()
        if suffix == '':
            return 'File'
        elif suffix in ['txt']:
            return 'Text File'
        elif suffix in ['jpg', 'jpeg', 'png', 'img', 'bmp']:
            return 'Image File'
        elif suffix in ['mp4', 'mpeg', 'mkv', 'flv']:
            return 'Video File'
        elif suffix in ['mp3', 'wav']:
            return 'Audio File'
        elif suffix in ['zip', 'rar', '7z', 'tar', 'gz']:
            return 'Archive File'
        else:
            return f'{suffix.upper()} File'


class StorageBucket(object):
    def __init__(self, bucket_id, dc_name=None):
        self.id = bucket_id
        self._session = get_easyun_session(dc_name)
        self._resource = self._session.resource('s3')
        self._client = self._session.client('s3')
        try:
            if vaildate_bucket_exist(bucket_id):
                self.bucketObj = self._resource.Bucket(self.id)
            else:
                raise ValueError(f'Bucket {bucket_id} does not exist.')
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        bucket = self.bucketObj
        try:
            bktEndpoint = self.get_bucket_endpoint()
            bktBasic = {
                'bucketId': self.id,
                'createTime': bucket.creation_date,
                'bucketRegion': bktEndpoint.get('bucketRegion'),
                'bucketUrl': bktEndpoint.get('bucketUrl')
            }
            pubBlockConfig = {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True,
            }
            bktPermission = {
                'bucketACL': 'private',
                'pubBlockConfig': pubBlockConfig
            }
            pubStatus = self.get_public_status()
            bktProperty = {
                'isEncryption': False,
                'isVersioning': False,
            }
            userTags = [
                {},
            ]

            bucketDetail = {
                'bucketBasic': bktBasic,
                'bucketPermission': bktPermission.update(pubStatus),
                'bucketProperty': bktProperty,
                'bucketSize': self.get_bucket_size(),
                'userTags': userTags
            }
            return bucketDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bucket_endpoint(self):
        '''查询存储桶(bucket)所处Region'''
        resp = self._client.get_bucket_location(Bucket=self.id)
        bktRegion = resp.get('LocationConstraint')
        # Buckets in Region us-east-1 have a LocationConstraint of null.
        if bktRegion is None:
            bktUrl = f'{self.id}.s3.amazonaws.com'
            bktRegion = 'east-us-1'
        else:
            bktUrl = f'{self.id}.s3.{bktRegion}.amazonaws.com'
        return {
            'bucketRegion': bktRegion,
            'bucketUrl': bktUrl
        }

    def get_bucket_size(self):
        '''查询存储桶(bucket)总容量'''
        try:
            client_cw = self._session.client('cloudwatch')
            nowDtime = datetime.now()

            bktMetric = client_cw.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'bucketId', 'Value': self.id},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'},
                ],
                # Statistics=['SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum',]
                Statistics=['Average'],
                EndTime=nowDtime,
                StartTime=nowDtime + timedelta(hours=-36),
                Period=86400,  # one day(24h)
                # Unit='Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'None'
            ).get('Datapoints')
            metricItem = bktMetric.pop()
            if metricItem:
                bktSize = {'value': metricItem['Average'], 'unit': metricItem['Unit']}
                return bktSize
            else:
                return {'value': None, 'unit': 'N/A'}
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_public_status(self):
        '''查询存储桶(bucket)公开状态'''
        privateMsg = 'All objects are private'
        publicMsg = 'Public'
        otherMsg = 'Objects can be public'
        try:
            # 获取当前Account ID
            thisAccount = Account.query.first()
            # step1: 判断Account Public Access Status
            client_s3ctr = self._session.client('s3control')
            accountPubConfig = client_s3ctr.get_public_access_block(
                AccountId=thisAccount.account_id
            ).get('PublicAccessBlockConfiguration')
            acnpubStatus = check_bucket_public(accountPubConfig)
            if acnpubStatus == 'private':
                return {'pubStatus': acnpubStatus, 'statusMsg': privateMsg}
            elif acnpubStatus == 'public':
                # step2: 判断Bucket Public Access Status
                bucketPubConfig = self._client.get_public_access_block(
                    Bucket=self.id
                ).get('PublicAccessBlockConfiguration')
                bucketPubStatus = check_bucket_public(bucketPubConfig)
                if bucketPubStatus == 'public':
                    pubStatus = {
                        'status': bucketPubStatus,
                        'description': publicMsg,
                    }
                elif bucketPubStatus == 'private':
                    pubStatus = {
                        'status': bucketPubStatus,
                        'description': privateMsg,
                    }
                else:
                    pubStatus = {
                        'status': bucketPubStatus,
                        'description': otherMsg,
                    }
            return pubStatus
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def query_bucket_lifecycle(self, bucket):
        try:
            bktRules = bucket.Lifecycle().rules
            bucketLifecycle = bktRules[0]
            return bucketLifecycle
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        bucket = self.bucketObj
        try:
            bucket.delete()
            bucket.wait_until_not_exists()
            oprtRes = {
                'operation': 'Delete Bucket',
                'bucketId': self.id
            }
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_encryption
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_bucket_encryption
    def set_default_encryption(self, bucket_id, encry_config='disable'):
        try:
            if encry_config == 'enable':
                self._client.put_bucket_encryption(
                    Bucket=bucket_id,
                    ServerSideEncryptionConfiguration={
                        'Rules': [
                            {
                                'ApplyServerSideEncryptionByDefault': {
                                    'SSEAlgorithm': 'AES256',
                                    # KMSMasterKeyID parameter is allowed only if SSEAlgorithm is set to aws:kms
                                    # 'KMSMasterKeyID': 'string'
                                },
                                'BucketKeyEnabled': False,
                            },
                        ]
                    },
                    # ChecksumAlgorithm='CRC32'|'CRC32C'|'SHA1'|'SHA256',
                    # ContentMD5='string',
                    # ExpectedBucketOwner='string'
                )
            elif encry_config == 'disable':
                self._client.delete_bucket_encryption(Bucket=bucket_id)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_encryption
    def set_public_access(self, bucket_id, block_config=None):
        try:
            if block_config is None:
                block_config = {
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True,
                }
            self._client.put_public_access_block(
                Bucket=bucket_id,
                PublicAccessBlockConfiguration=block_config,
            )
            return True
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_objects(self):
        paginator = self._client.get_paginator('list_objects_v2')
        try:
            resIterator = paginator.paginate(Bucket=self.id)
            objectList = []
            for page in resIterator:
                if 'Contents' in page:
                    for obj in page.get('Contents'):
                        objDict = {
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'type': get_file_type(obj['Key']),
                            'storageClass': obj['StorageClass'],
                            'modifiedTime': obj['LastModified'],
                            'eTag': obj['ETag']
                        }
                        objectList.append(objDict)
            return objectList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
