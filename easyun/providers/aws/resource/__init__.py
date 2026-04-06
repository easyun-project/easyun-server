# -*- coding: utf-8 -*-
"""
  @module:  Cloud Resource SDK Module
  @desc:    AWS SDK Boto3 Resource Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from .compute.sdk_server import EC2Server
from .storage.sdk_volume import StorageVolume
from .storage.sdk_bucket import StorageBucket, query_bucket_flag
from .database.sdk_database import DBInstance
from .network.sdk_loadbalancer import LoadBalancer
from ..session import get_easyun_session
from easyun.providers.aws.utils import get_server_name


def get_ec2_server(svr_id, dc_name):
    return EC2Server(svr_id, dc_name)


def get_st_volume(volume_id, dc_name):
    return StorageVolume(volume_id, dc_name)


def get_st_bucket(bucket_id, dc_name=None):
    return StorageBucket(bucket_id, dc_name)


def get_db_instance(dbi_id, dc_name):
    return DBInstance(dbi_id, dc_name)


def get_load_balancer(elb_id, dc_name):
    return LoadBalancer(elb_id, dc_name)


class Resource(object):
    def __init__(self, dc_name):
        self._session = get_easyun_session(dc_name)
        self.dcName = dc_name
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dc_name]}
        self.flagTag = {'Key': 'Flag', "Value": dc_name}

    def list_all_server(self):
        """列出 datacenter 下所有 server 详细信息"""
        resource = self._session.resource('ec2')
        client = resource.meta.client
        try:
            svrIterator = resource.instances.filter(Filters=[self.tagFilter])
            svrList = []
            for s in svrIterator:
                nameTag = next((tag['Value'] for tag in (s.tags or []) if tag['Key'] == 'Name'), None)
                volumeSize = sum(
                    resource.Volume(d['Ebs']['VolumeId']).size
                    for d in s.block_device_mappings
                )
                insInfo = client.describe_instance_types(InstanceTypes=[s.instance_type])
                ramSize = insInfo['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']
                instDetail = client.describe_instances(InstanceIds=[s.id])
                instRes = [j for i in instDetail['Reservations'] for j in i['Instances']][0]
                association = instRes['NetworkInterfaces'][0].get('Association') if instRes.get('NetworkInterfaces') else None
                try:
                    osName = resource.Image(s.image_id).platform_details
                except Exception:
                    osName = 'unknown'
                svrList.append({
                    'svrId': s.id,
                    'tagName': nameTag,
                    'svrState': s.state['Name'],
                    'insType': s.instance_type,
                    'vpuNum': s.cpu_options['CoreCount'],
                    'ramSize': ramSize / 1024,
                    'volumeSize': volumeSize,
                    'osName': osName,
                    'azName': s.placement.get('AvailabilityZone'),
                    'pubIp': s.public_ip_address,
                    'priIp': s.private_ip_address,
                    'isEip': bool(association and association.get('IpOwnerId') != 'amazon'),
                })
            return svrList
        except Exception as ex:
            raise ex

    def list_server_brief(self):
        """列出 datacenter 下所有 server 基础信息"""
        resource = self._session.resource('ec2')
        try:
            svrIterator = resource.instances.filter(Filters=[self.tagFilter])
            return [
                {
                    'svrId': s.id,
                    'tagName': next((tag['Value'] for tag in (s.tags or []) if tag['Key'] == 'Name'), None),
                    'svrState': s.state['Name'],
                    'insType': s.instance_type,
                    'azName': s.placement.get('AvailabilityZone'),
                }
                for s in svrIterator
            ]
        except Exception as ex:
            raise ex


    def create_server(self, parm):
        """创建 EC2 实例"""
        resource = self._session.resource('ec2')
        flagTag = {'Key': 'Flag', 'Value': self.dcName}
        nameTag = {'Key': 'Name', 'Value': parm['tagName']}
        servers = resource.create_instances(
            MaxCount=parm.get('svrNumber', 1),
            MinCount=parm.get('svrNumber', 1),
            ImageId=parm['ImageId'],
            InstanceType=parm['InstanceType'],
            SubnetId=parm['SubnetId'],
            SecurityGroupIds=parm['SecurityGroupIds'],
            KeyName=parm['KeyName'],
            BlockDeviceMappings=parm['BlockDeviceMappings'],
            TagSpecifications=[
                {'ResourceType': 'instance', 'Tags': [flagTag, nameTag]},
                {'ResourceType': 'volume', 'Tags': [flagTag, nameTag]},
            ],
        )
        return [
            {
                'svrId': s.id,
                'insTpye': s.instance_type,
                'createTime': s.launch_time.isoformat(),
                'svrState': s.state['Name'],
                'priIp': s.private_ip_address,
            }
            for s in servers
        ]
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


    def create_bucket_cc(self, bucket_id, region, options):
        """通过 CloudControl 创建 S3 Bucket"""
        client_cc = self._session.client('cloudcontrol', region_name=region)
        desired_state = {
            'bucketId': bucket_id,
            'VersioningConfiguration': {'Status': 'Enabled' if options.get('isVersioning') else 'Suspended'},
            'PublicAccessBlockConfiguration': {
                'BlockPublicAcls': True, 'IgnorePublicAcls': True,
                'BlockPublicPolicy': True, 'RestrictPublicBuckets': True,
            },
            'Tags': [self.flagTag],
        }
        if options.get('isEncryption'):
            desired_state['BucketEncryption'] = {
                'ServerSideEncryptionConfiguration': [{
                    'BucketKeyEnabled': True,
                    'ServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'},
                }]
            }
        result = client_cc.create_resource(TypeName='AWS::S3::Bucket', DesiredState=str(desired_state))
        return result['ProgressEvent']
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
