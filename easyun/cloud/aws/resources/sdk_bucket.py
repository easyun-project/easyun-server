# -*- coding: utf-8 -*-
"""
  @module:  Bucket (S3) SDK Module
  @desc:    AWS SDK Boto3 EC2 Client and Resource Wrapper. 
  @auth:
"""
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
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


def check_bucket_public(config):
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


class StorageBucket(object):
    def __init__(self, dcName):
        self.dcName = dcName
        self._session = get_easyun_session(dcName)
        self._resource = self._session.resource('s3')
        self._client = self._session.client('s3')
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dcName]}

    def list_all_bucket(self):
        try:
            bucketList = []
            allBuckets = self._resource.buckets.all()
            for bkt in allBuckets:
                if query_bucket_flag(bkt) == self.dcName:
                    bktDomain = self.get_bucket_domain(bkt.name)
                    bktItem = {
                        'bucketId': bkt.name,
                        'createTime': bkt.creation_date,
                        'bucketRegion': bktDomain.get('bucketRegion'),
                        'bucketUrl': bktDomain.get('bucketUrl'),
                        # 'bucketSize': self.query_bucket_size(bkt.name),
                        'bucketAccess': {
                            'status': 'private',
                            'description': 'All objects are private',
                        },
                        'bucketSize': {'value': 123, 'unit': 'MiB'},
                    }
                    # bktItem.update(self.query_bucket_public(bkt.name))
                    bucketList.append(bktItem)
            return bucketList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bucket_list(self):
        try:
            bucketList = []
            allBuckets = self._resource.buckets.all()
            for bkt in allBuckets:
                if query_bucket_flag(bkt) == self.dcName:
                    bucketList.append(
                        {
                            'bucketId': bkt.name,
                            'createTime': bkt.creation_date,
                            'bucketRegion': self.get_bucket_domain(bkt.name)[
                                'bucketRegion'
                            ],
                        }
                    )
            return bucketList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bucket_detail(self, bucket_id):
        try:
            bucket = self._resource.Bucket(bucket_id)
            bktDomain = self.get_bucket_domain(bucket_id)
            bktBasic = {
                'bucketId': bucket_id,
                'createTime': bucket.creation_date,
                'bucketRegion': bktDomain.get('bucketRegion'),
                'bucketUrl': bktDomain.get('bucketUrl'),
            }
            bktPermission = {
                'status': 'private',
                'description': 'All objects are private',
                'bucketACL': 'private',
                'pubBlockConfig': {
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True,
                },
            }
            bktProperty = {
                'isEncryption': False,
                'isVersioning': False,
            }

            bucketDetail = {
                'bucketBasic': bktBasic,
                'bucketPermission': bktPermission,
                'bucketProperty': bktProperty,
                'userTags': {},
            }

            return bucketDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bucket_domain(self, bucket_id):
        '''查询存储桶(bucket)所处Region'''
        resp = self._client.get_bucket_location(Bucket=bucket_id)
        bktRegion = resp.get('LocationConstraint')
        # Buckets in Region us-east-1 have a LocationConstraint of null.
        if bktRegion is None:
            bktUrl = f'{bucket_id}.s3.amazonaws.com'
            bktRegion = 'east-us-1'
        else:
            bktUrl = f'{bucket_id}.s3.{bktRegion}.amazonaws.com'
        return {'bucketRegion': bktRegion, 'bucketUrl': bktUrl}

    def query_bucket_size(self, bucket_id):
        '''查询存储桶(bucket)总容量'''
        try:
            client_cw = self._session.client('cloudwatch')
            nowDtime = datetime.now()

            bktMetric = client_cw.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'bucketId', 'Value': bucket_id},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'},
                ],
                #   Statistics=['SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum',]
                Statistics=['Average'],
                EndTime=nowDtime,
                StartTime=nowDtime + timedelta(hours=-36),
                Period=86400,  # one day(24h)
                #     Unit='Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'None'
            ).get('Datapoints')
            metricItem = bktMetric.pop()
            if metricItem:
                bktSize = {'value': metricItem['Average'], 'unit': metricItem['Unit']}
                return bktSize
            else:
                return {'value': None, 'unit': 'N/A'}
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def query_bucket_public(self, bucket_id):
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
                    Bucket=bucket_id
                ).get('PublicAccessBlockConfiguration')
                bucketPubStatus = check_bucket_public(bucketPubConfig)
                if bucketPubStatus == 'public':
                    pubStatus = {
                        'publicStatus': bucketPubStatus,
                        'publicMessage': publicMsg,
                    }
                elif bucketPubStatus == 'private':
                    pubStatus = {
                        'publicStatus': bucketPubStatus,
                        'publicMessage': privateMsg,
                    }
                else:
                    pubStatus = {
                        'publicStatus': bucketPubStatus,
                        'publicMessage': otherMsg,
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

    def vaildate_bucket_name(self, bucket_id):
        try:
            bucket = self._resource.Bucket(bucket_id)
            isAvailable = False if bucket.creation_date else True
            return isAvailable
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_bucket(self, bucket_id, options):
        try:
            # step1: 新建Bucket
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.create_bucket
            region = options.get('regionCode')
            location = {'LocationConstraint': region}
            newBucket = self._resource.create_bucket(
                Bucket=bucket_id,
                CreateBucketConfiguration=location,
                # ACL='private'|'public-read'|'public-read-write'|'authenticated-read',
                # GrantFullControl='string',
                # GrantRead='string',
                # GrantReadACP='string',
                # GrantWrite='string',
                # GrantWriteACP='string',
                # ObjectLockEnabledForBucket=True|False,
                # ObjectOwnership='BucketOwnerPreferred'|'ObjectWriter'|'BucketOwnerEnforced'
            )
            newBucket.wait_until_exists(
                # ExpectedBucketOwner='string'
            )

            # step2: 设置Bucket default encryption，默认不启用
            if options.get('isEncryption'):
                self.set_default_encryption(bucket_id, 'enable')

            # step3: 设置Bucket Versioning，默认不启用
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#bucketversioning
            if options.get('isVersioning'):
                bucketVersion = self._resource.BucketVersioning(bucket_id)
                bucketVersion.enable()

            # step4: 设置Bucket Tag:Flag 标签
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#buckettagging
            bucketTagging = self._resource.BucketTagging(bucket_id)
            bucketTagging.put(
                Tagging={
                    'TagSet': [
                        {'Key': 'Flag', 'Value': self.dcName},
                    ]
                }
            )

            # step5:  设置Bucket public access默认private
            block_config = options.get('pubBlockConfig')
            self.set_public_access(bucket_id, block_config)

            return newBucket
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete_bucket(self, bucket_id):
        try:
            thisBucket = self._resource.Bucket(bucket_id)
            thisBucket.delete()
            thisBucket.wait_until_not_exists()
            return True
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
