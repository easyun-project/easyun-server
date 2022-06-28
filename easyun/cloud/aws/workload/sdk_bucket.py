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
    '''检查存储桶公开访问状态(基于PublicAccessBlock)'''
    if block_config:
        if block_config.get('IgnorePublicAcls') or block_config.get('isBlockAllAcls'):
            accessStatus = 'private'
        elif not (block_config.get('IgnorePublicAcls') or block_config.get('isBlockAllAcls')):
            accessStatus = 'public'
        else:
            accessStatus = 'other'
    else:
        accessStatus = 'other'
    return accessStatus


def vaildate_bucket_exist(bucket_id, dc_name=None):
    '''检查bucket是否存在且有权访问'''
    session = get_easyun_session(dc_name)
    try:
        # bucket = session.resource('s3').Bucket(bucket_id)
        # isExist = True if bucket.creation_date else False
        s3_client = session.client('s3')
        resp = s3_client.head_bucket(Bucket=bucket_id)
        return True if resp else False
    except ClientError:
        return False


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
            bktBasic = {
                'bucketId': self.id,
                'createTime': bucket.creation_date,
            }
            bktBasic.update(self.get_bkt_endpoint())

            bktPermission = {
                'bucketACL': 'private',
                'pubBlockConfig': self.get_public_config()
            }
            bktPermission.update(self.get_public_status())

            bktProperty = {
                'isEncryption': self.get_bkt_encryption(),
                'isVersioning': self.get_bkt_versioning(),
            }
            bktTags = self._client.get_bucket_tagging(Bucket=self.id).get('TagSet')
            userTags = [t for t in bktTags if t['Key'] not in ['Flag', 'Name']]

            bucketDetail = {
                'bucketBasic': bktBasic,
                'bucketPermission': bktPermission,
                'bucketProperty': bktProperty,
                'bucketSize': self.get_bkt_size(),
                'userTags': userTags
            }
            return bucketDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bkt_endpoint(self):
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

    def get_bkt_versioning(self):
        '''获取存储桶(bucket)Versioning设置信息'''
        try:
            resp = self._client.get_bucket_versioning(Bucket=self.id)
            verStatus = resp.get('Status')
            return True if verStatus == 'Enabled' else False
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bkt_encryption(self):
        '''获取存储桶(bucket)Encryption设置信息'''
        try:
            resp = self._client.get_bucket_encryption(Bucket=self.id)
            encStatus = resp.get('ServerSideEncryptionConfiguration')
            return True if encStatus else False
        except ClientError:
            return False

    def get_bkt_size(self):
        '''获取存储桶(bucket)总容量'''
        paginator = self._client.get_paginator('list_objects_v2')
        try:
            resIterator = paginator.paginate(Bucket=self.id)
            summSize = 0
            for page in resIterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        summSize += obj.get('Size')
            return {
                'value': summSize/1024,
                'unit': 'KiB'
            }
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bkt_size_cw(self):
        '''从Cloudwatch查询存储桶(bucket)总容量 【fix-me】'''
        try:
            cw_client = self._session.client('cloudwatch')
            currTime = datetime.now()

            bktMetric = cw_client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'bucketId', 'Value': self.id},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'},
                ],
                # Statistics=['SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum',]
                Statistics=['Average'],
                EndTime=currTime,
                StartTime=currTime - timedelta(days=1),
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

    def get_lifecycle_rules(self, bucket):
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

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_versioning
    def set_bkt_versioning(self, is_versioning=True):
        verStatus = 'Enabled' if is_versioning else 'Suspended'
        try:
            self._client.put_bucket_versioning(
                Bucket=self.id,
                VersioningConfiguration={
                    'Status': verStatus,
                    # 'MFADelete': 'Disabled'
                }
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_encryption
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_bucket_encryption
    def set_default_encryption(self, is_encryption=True):
        try:
            if is_encryption:
                self._client.put_bucket_encryption(
                    Bucket=self.id,
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
            else:
                self._client.delete_bucket_encryption(Bucket=self.id)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_public_config(self):
        '''查询存储桶(bucket)公开状态'''
        try:
            pubConfig = self._client.get_public_access_block(
                Bucket=self.id
            ).get('PublicAccessBlockConfiguration')
            return {
                'isBlockNewAcls': pubConfig['BlockPublicAcls'],
                'isBlockAllAcls': pubConfig['IgnorePublicAcls'],
                'isBlockNewPolicy': pubConfig['BlockPublicPolicy'],
                'isBlockAllPolicy': pubConfig['RestrictPublicBuckets'],
            }
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_public_status(self):
        '''查询存储桶(bucket)公开状态'''
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
                return {
                    'status': acnpubStatus,
                    'description': 'All objects are private'
                }
            elif acnpubStatus == 'public':
                # step2: 判断Bucket Public Access Status
                bucketPubConfig = self.get_public_config()
                bucketPubStatus = check_bucket_public(bucketPubConfig)
                if bucketPubStatus == 'public':
                    pubStatus = {
                        'status': bucketPubStatus,
                        'description': 'Public',
                    }
                elif bucketPubStatus == 'private':
                    pubStatus = {
                        'status': bucketPubStatus,
                        'description': 'All objects are private',
                    }
                else:
                    pubStatus = {
                        'status': bucketPubStatus,
                        'description': 'Objects can be public',
                    }
            return pubStatus
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_encryption
    def set_public_access(self, pub_config=None):
        try:
            if pub_config is None:
                publicAccessBlock = {
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True,
                }
            else:
                publicAccessBlock = {
                    'BlockPublicAcls': pub_config['isBlockNewAcls'],
                    'IgnorePublicAcls': pub_config['isBlockAllAcls'],
                    'BlockPublicPolicy': pub_config['isBlockNewPolicy'],
                    'RestrictPublicBuckets': pub_config['isBlockAllPolicy'],
                }
            self._client.put_public_access_block(
                Bucket=self.id,
                PublicAccessBlockConfiguration=publicAccessBlock,
            )
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


class StorageObject(object):
    def __init__(self, object_key, bucket_id):
        self.key = object_key
        try:
            self.bucket = StorageBucket(bucket_id)
            self.objectObj = self.bucket.bucketObj.Object(self.d)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#object
    def get_attributes(self):
        '''Get object's available attributes'''
        object = self.objectObj
        try:
            return object
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.head_object
    def get_metadata(self):
        '''Retrieves metadata from an object without returning the object itself.'''
        client = self.bucket._client
        try:
            objectMeta = client.head_object(
                Bucket=self.bucket.id,
                Key=self.key,
                IfMatch='string',
                IfModifiedSince=datetime(2015, 1, 1),
                IfNoneMatch='string',
                IfUnmodifiedSince=datetime(2015, 1, 1),
                Range='string',
                VersionId='string',
                SSECustomerAlgorithm='string',
                SSECustomerKey='string',
                RequestPayer='requester',
                PartNumber=123,
                ExpectedBucketOwner='string',
                ChecksumMode='ENABLED'
            )
            return objectMeta
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
