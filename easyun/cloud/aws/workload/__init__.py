# -*- coding: utf-8 -*-
"""
  @module:  Datacenter Resources SDK Module
  @desc:    AWS SDK Boto3 Resources Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from .sdk_server import EC2Server
from .sdk_volume import StorageVolume
from .sdk_bucket import StorageBucket, query_bucket_flag
from .sdk_database import DBInstance
from .sdk_loadbalancer import LoadBalancer
from ..session import get_easyun_session
from easyun.cloud.utils import get_server_name


_EC2_SERVER = None
_STORAGE_VOLUME = None
_STORAGE_BUCKET = None
_DB_INSTANCE = None
_LOAD_BALANCER = None


def get_ec2_server(svr_id, dc_name):
    global _EC2_SERVER
    if _EC2_SERVER is not None and _EC2_SERVER.id == svr_id:
        return _EC2_SERVER
    else:
        return EC2Server(svr_id, dc_name)


def get_st_volume(volume_id, dc_name):
    global _STORAGE_VOLUME
    if _STORAGE_VOLUME is not None and _STORAGE_VOLUME.id == volume_id:
        return _STORAGE_VOLUME
    else:
        return StorageVolume(volume_id, dc_name)


def get_st_bucket(bucket_id, dc_name=None):
    global _STORAGE_BUCKET
    if _STORAGE_BUCKET is not None and _STORAGE_BUCKET.id == bucket_id:
        return _STORAGE_BUCKET
    else:
        return StorageBucket(bucket_id, dc_name)


def get_db_instance(dbi_id, dc_name):
    global _DB_INSTANCE
    if _DB_INSTANCE is not None and _DB_INSTANCE.id == dbi_id:
        return _DB_INSTANCE
    else:
        return DBInstance(dbi_id, dc_name)


def get_load_balancer(elb_id, dc_name):
    global _LOAD_BALANCER
    if _LOAD_BALANCER is not None and _LOAD_BALANCER.id == elb_id:
        return _LOAD_BALANCER
    else:
        return LoadBalancer(elb_id, dc_name)


class Workload(object):
    def __init__(self, dc_name):
        self._session = get_easyun_session(dc_name)
        self.dcName = dc_name
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dc_name]}
        self.flagTag = {'Key': 'Flag', "Value": dc_name}

    def list_all_volume(self):
        resource = self._session.resource('ec2')
        try:
            volIterator = resource.volumes.filter(Filters=[self.tagFilter])
            volumeList = []
            for vol in volIterator:
                nameTag = next(
                    (tag['Value'] for tag in vol.tags if tag["Key"] == 'Name'), None
                )
                attachList = []
                attachs = vol.attachments
                if attachs:
                    # 定义系统盘路径
                    SYSTEMDISK_PATH = ['/dev/xvda', '/dev/sda1']
                    for a in attachs:
                        # 基于卷挂载路径判断disk类型是 system 还是 user
                        diskType = (
                            'system' if a['Device'] in SYSTEMDISK_PATH else 'user'
                        )
                        attachList.append(
                            {
                                'attachPath': a['Device'],
                                'svrId': a['InstanceId'],
                                'tagName': get_server_name(a['InstanceId']),
                                'attachTime': a['AttachTime'],
                                'diskType': diskType,
                            }
                        )
                isAttachable = (
                    True
                    if vol.multi_attach_enabled or vol.state == 'available'
                    else False
                )
                volItem = {
                    'volumeId': vol.id,
                    'tagName': nameTag,
                    'volumeState': vol.state,
                    'isAttachable': isAttachable,
                    'volumeAz': vol.availability_zone,
                    'createTime': vol.create_time,
                    'volumeType': vol.volume_type,
                    'volumeSize': vol.size,
                    'volumeIops': vol.iops,
                    'volumeThruput': vol.throughput,
                    'isEncrypted': vol.encrypted,
                    'isMultiAttach': vol.multi_attach_enabled,
                    #             'usedSize': none,
                    'volumeAttach': attachList,
                }
                volumeList.append(volItem)
            return volumeList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_volume_list(self):
        resource = self._session.resource('ec2')
        try:
            volIterator = resource.volumes.filter(Filters=[self.tagFilter])
            volumeList = []
            for vol in volIterator:
                nameTag = next(
                    (tag['Value'] for tag in vol.tags if tag["Key"] == 'Name'), None
                )
                isAttachable = (
                    True
                    if vol.multi_attach_enabled or vol.state == 'available'
                    else False
                )
                volItem = {
                    'volumeId': vol.id,
                    'tagName': nameTag,
                    'isAttachable': isAttachable,
                    'volumeState': vol.state,
                    'volumeAz': vol.availability_zone,
                    'volumeType': vol.volume_type,
                    'volumeSize': vol.size,
                    'createTime': vol.create_time,
                }
                volumeList.append(volItem)
            return volumeList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_bucket(self):
        s3 = self._session.resource('s3')
        try:
            bucketList = []
            buckets = s3.buckets.all()
            for bucket in buckets:
                if query_bucket_flag(bucket) == self.dcName:
                    bkt = StorageBucket(bucket.name)
                    bktEndpoint = bkt.get_bkt_endpoint()
                    bktItem = {
                        'bucketId': bucket.name,
                        'createTime': bucket.creation_date,
                        'bucketRegion': bktEndpoint['bucketRegion'],
                        'bucketUrl': bktEndpoint['bucketUrl'],
                        # 'bucketAccess': bkt.get_public_status(),
                        'bucketAccess': {
                            'status': 'private',
                            'description': 'All objects are private',
                        },
                    }
                    # bktItem.update(self.query_bucket_public(bkt.name))
                    bucketList.append(bktItem)
            return bucketList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_bucket_list(self):
        s3 = self._session.resource('s3')
        try:
            bucketList = []
            buckets = s3.buckets.all()
            for bucket in buckets:
                if query_bucket_flag(bucket) == self.dcName:
                    bkt = StorageBucket(bucket.name)
                    bucketList.append(
                        {
                            'bucketId': bucket.name,
                            'createTime': bucket.creation_date,
                            'bucketRegion': bkt.get_bkt_endpoint()['bucketRegion'],
                        }
                    )
            return bucketList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_dbinstance(self):
        client = self._session.client('rds')
        try:      
            dbis = client.describe_db_instances(
                # Filters=[self.tagFilter]
            )['DBInstances']
            dbiList = []
            for dbi in dbis:
                # filter不支持tag过滤条件，手动判断Flag标记
                flagTag = next((tag['Value'] for tag in dbi['TagList'] if tag["Key"] == 'Flag'), None)
                if flagTag == self.dcName:
                    dbiItem = {
                        'dbiId': dbi['DBInstanceIdentifier'],
                        'dbiEngine': dbi['Engine'],
                        'engineVer': dbi['EngineVersion'],
                        'dbiStatus': 'available',
                        'dbiSize': dbi['DBInstanceClass'],
                        'vcpuNum': 1,
                        'ramSize': 2,
                        'volumeSize': 20,
                        'dbiAz': dbi['AvailabilityZone'],
                        'multiAz': dbi['MultiAZ'],
                        'dbiEndpoint': dbi['Endpoint'].get('Address'),
                        # 'createTime': dbi['InstanceCreateTime'].isoformat()
                    }
                    dbiList.append(dbiItem)
            return dbiList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_dbinstance_list(self):
        client = self._session.client('rds')
        try:      
            dbis = client.describe_db_instances(
                # Filters=[self.tagFilter]
            )['DBInstances']
            dbiList = []
            for dbi in dbis:
                # filter不支持tag过滤条件，手动判断Flag标记
                flagTag = next((tag['Value'] for tag in dbi['TagList'] if tag["Key"] == 'Flag'), None)
                if flagTag == self.dcName:
                    dbiItem = {
                        'dbiId': dbi['DBInstanceIdentifier'],
                        'dbiEngine': dbi['Engine'],
                        'dbiStatus': 'available',
                        'dbiSize': dbi['DBInstanceClass'],
                        'dbiAz': dbi['AvailabilityZone'],
                    }
                    dbiList.append(dbiItem)
            return dbiList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_loadbalancer(self):
        client = self._session.client('elbv2')
        try:
            elbs = client.describe_load_balancers(
                # Filters=[self.tagFilter]
            )['LoadBalancers']
            elbList = []
            for elb in elbs:
                # nameTag = 'to_be_done'
                elbAzList = []
                for i in elb.get('AvailabilityZones'):
                    elbAzList.append(
                        {
                            'azName': i['ZoneName'],
                            'subnetId': i['SubnetId'],
                            'elbAddresses': i['LoadBalancerAddresses'],
                        }
                    )
                elbItem = {
                    'elbId': elb['LoadBalancerName'],
                    # 'tagName': nameTag,
                    'dnsName': elb['DNSName'],
                    'elbArn': elb['LoadBalancerArn'],
                    'elbAzs': elbAzList,
                    'ipType': elb['IpAddressType'],
                    'elbType': elb['Type'],
                    'elbState': elb['State']['Code'],
                    'elbScheme': elb['Scheme'],
                    # 'vpcId': elb['VpcId'],
                    'secGroups': elb['SecurityGroups'],
                    'createTime': elb['CreatedTime'],
                }
                elbList.append(elbItem)
            return elbList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_loadbalancer_list(self):
        client = self._session.client('elbv2')
        try:
            elbs = client.describe_load_balancers(
                # Filters=[self.tagFilter]
            )['LoadBalancers']
            elbList = []
            for elb in elbs:
                # nameTag = 'to_be_done'
                elbItem = {
                    'elbId': elb['LoadBalancerName'],
                    'elbArn': elb['LoadBalancerArn'],
                    # 'tagName': nameTag,
                    'dnsName': elb['DNSName'],
                    'elbType': elb['Type'],
                    'elbState': elb['State']['Code'],
                    'elbScheme': elb['Scheme'],
                }
                elbList.append(elbItem)
            return elbList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_bucket(self, bucket_id, options):
        s3 = self._session.resource('s3')
        try:
            # step1: 新建Bucket
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.create_bucket
            region = options.get('regionCode')
            s3Bucket = s3.create_bucket(
                Bucket=bucket_id,
                CreateBucketConfiguration={'LocationConstraint': region},
                # ACL='private'|'public-read'|'public-read-write'|'authenticated-read',
                # GrantFullControl='string',
                # GrantRead='string',
                # GrantReadACP='string',
                # GrantWrite='string',
                # GrantWriteACP='string',
                # ObjectLockEnabledForBucket=True|False,
                # ObjectOwnership='BucketOwnerPreferred'|'ObjectWriter'|'BucketOwnerEnforced'
            )
            s3Bucket.wait_until_exists()
            newBucket = StorageBucket(s3Bucket.name)

            # step2: 设置 Bucket default encryption，默认不启用
            if 'isEncryption' in options:
                newBucket.set_default_encryption(options['isEncryption'])

            # step3: 设置Bucket Versioning，默认不启用
            if 'isVersioning' in options:
                newBucket.set_bkt_versioning(options['isVersioning'])

            # step4:  设置Bucket public access默认private
            pubConfig = options.get('pubBlockConfig')
            newBucket.set_public_access(pubConfig)

            # step5: 设置Bucket Tag:Flag 标签
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#buckettagging
            bucketTagging = s3.BucketTagging(bucket_id)
            bucketTagging.put(
                Tagging={
                    'TagSet': [
                        {'Key': 'Flag', 'Value': self.dcName},
                    ]
                }
            )
            return newBucket
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_volume(
        self, vol_type, vol_size, vol_zone,
        iops=None,
        throughput=None,
        is_multiattach=None,
        is_encrypted=None,
        tag_name=None,
    ):
        client = self._session.client('ec2')
        nameTag = {"Key": "Name", "Value": tag_name}
        tagSpecifications = [
            {"ResourceType": "volume", "Tags": [self.flagTag, nameTag]}
        ]
        try:
            # 基于voluem type执行不同的创建参数
            if vol_type in ['gp3']:
                ebsVolume = client.create_volume(
                    VolumeType=vol_type,
                    Size=vol_size,
                    AvailabilityZone=vol_zone,
                    Encrypted=is_encrypted,
                    TagSpecifications=tagSpecifications,
                    Iops=iops,
                    Throughput=throughput,
                )
            elif vol_type in ['io1', 'io2']:
                ebsVolume = client.create_volume(
                    VolumeType=vol_type,
                    Size=vol_size,
                    AvailabilityZone=vol_zone,
                    Encrypted=is_encrypted,
                    TagSpecifications=tagSpecifications,
                    Iops=iops,
                    MultiAttachEnabled=is_multiattach,
                )
            else:  # ['gp2','sc1','st1','standard']
                ebsVolume = client.create_volume(
                    VolumeType=vol_type,
                    Size=vol_size,
                    AvailabilityZone=vol_zone,
                    Encrypted=is_encrypted,
                    TagSpecifications=tagSpecifications,
                )
            # wait until the volume is available
            waiter = client.get_waiter('volume_available')
            waiter.wait(VolumeIds=[ebsVolume['VolumeId']])
            newVolume = StorageVolume(ebsVolume['VolumeId'])
            return newVolume
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
