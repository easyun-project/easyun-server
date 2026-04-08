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
from easyun.cloud.aws.utils import get_server_name


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
        from easyun.cloud.models import ServerDetail
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
                svrList.append(ServerDetail(
                    id=s.id,
                    name=nameTag,
                    state=s.state['Name'],
                    instance_type=s.instance_type,
                    az=s.placement.get('AvailabilityZone'),
                    vcpu=s.cpu_options['CoreCount'],
                    memory_gib=ramSize / 1024,
                    volume_size_gib=volumeSize,
                    os_name=osName,
                    public_ip=s.public_ip_address,
                    private_ip=s.private_ip_address,
                    is_eip=bool(association and association.get('IpOwnerId') != 'amazon'),
                ))
            return svrList
        except Exception as ex:
            raise ex

    def list_server_brief(self):
        """列出 datacenter 下所有 server 基础信息"""
        from easyun.cloud.models import ServerBrief
        resource = self._session.resource('ec2')
        try:
            svrIterator = resource.instances.filter(Filters=[self.tagFilter])
            return [
                ServerBrief(
                    id=s.id,
                    name=next((tag['Value'] for tag in (s.tags or []) if tag['Key'] == 'Name'), None),
                    state=s.state['Name'],
                    instance_type=s.instance_type,
                    az=s.placement.get('AvailabilityZone'),
                )
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
        from easyun.cloud.models import VolumeDetail
        resource = self._session.resource('ec2')
        try:
            volIterator = resource.volumes.filter(Filters=[self.tagFilter])
            volumeList = []
            for vol in volIterator:
                nameTag = next((tag['Value'] for tag in vol.tags if tag['Key'] == 'Name'), None)
                attachList = []
                if vol.attachments:
                    SYSTEMDISK_PATH = ['/dev/xvda', '/dev/sda1']
                    for a in vol.attachments:
                        attachList.append({
                            'attachPath': a['Device'],
                            'svrId': a['InstanceId'],
                            'tagName': get_server_name(a['InstanceId']),
                            'attachTime': a['AttachTime'],
                            'diskType': 'system' if a['Device'] in SYSTEMDISK_PATH else 'user',
                        })
                volumeList.append(VolumeDetail(
                    id=vol.id, name=nameTag, state=vol.state,
                    az=vol.availability_zone, volume_type=vol.volume_type,
                    size_gib=vol.size, is_attachable=bool(vol.multi_attach_enabled or vol.state == 'available'),
                    create_time=vol.create_time,
                    iops=vol.iops, throughput=vol.throughput,
                    is_encrypted=vol.encrypted, is_multi_attach=vol.multi_attach_enabled,
                    attachments=attachList,
                ))
            return volumeList
        except Exception as ex:
            raise ex

    def get_volume_list(self):
        from easyun.cloud.models import VolumeBrief
        resource = self._session.resource('ec2')
        try:
            volIterator = resource.volumes.filter(Filters=[self.tagFilter])
            return [
                VolumeBrief(
                    id=vol.id,
                    name=next((tag['Value'] for tag in vol.tags if tag['Key'] == 'Name'), None),
                    state=vol.state, az=vol.availability_zone,
                    volume_type=vol.volume_type, size_gib=vol.size,
                    is_attachable=bool(vol.multi_attach_enabled or vol.state == 'available'),
                    create_time=vol.create_time,
                )
                for vol in resource.volumes.filter(Filters=[self.tagFilter])
            ]
        except Exception as ex:
            raise ex

    def list_all_bucket(self):
        from easyun.cloud.models import BucketDetail
        s3 = self._session.resource('s3')
        try:
            bucketList = []
            for bucket in s3.buckets.all():
                if query_bucket_flag(bucket) == self.dcName:
                    bkt = StorageBucket(bucket.name)
                    ep = bkt.get_bkt_endpoint()
                    bucketList.append(BucketDetail(
                        id=bucket.name, region=ep['bucketRegion'],
                        create_time=bucket.creation_date, url=ep['bucketUrl'],
                        access={'status': 'private', 'description': 'All objects are private'},
                    ))
            return bucketList
        except ClientError as ex:
            raise ex

    def get_bucket_list(self):
        from easyun.cloud.models import BucketBrief
        s3 = self._session.resource('s3')
        try:
            bucketList = []
            for bucket in s3.buckets.all():
                if query_bucket_flag(bucket) == self.dcName:
                    bkt = StorageBucket(bucket.name)
                    bucketList.append(BucketBrief(
                        id=bucket.name, region=bkt.get_bkt_endpoint()['bucketRegion'],
                        create_time=bucket.creation_date,
                    ))
            return bucketList
        except ClientError as ex:
            raise ex

    def list_all_dbinstance(self):
        from easyun.cloud.models import DBInstanceDetail
        client = self._session.client('rds')
        try:
            dbis = client.describe_db_instances()['DBInstances']
            dbiList = []
            for dbi in dbis:
                flagTag = next((tag['Value'] for tag in dbi['TagList'] if tag['Key'] == 'Flag'), None)
                if flagTag == self.dcName:
                    dbiList.append(DBInstanceDetail(
                        id=dbi['DBInstanceIdentifier'], engine=dbi['Engine'],
                        engine_version=dbi['EngineVersion'], status='available',
                        instance_class=dbi['DBInstanceClass'],
                        az=dbi['AvailabilityZone'], multi_az=dbi['MultiAZ'],
                        endpoint=dbi['Endpoint'].get('Address', ''),
                    ))
            return dbiList
        except ClientError as ex:
            raise ex

    def get_dbinstance_list(self):
        from easyun.cloud.models import DBInstanceBrief
        client = self._session.client('rds')
        try:
            dbis = client.describe_db_instances()['DBInstances']
            dbiList = []
            for dbi in dbis:
                flagTag = next((tag['Value'] for tag in dbi['TagList'] if tag['Key'] == 'Flag'), None)
                if flagTag == self.dcName:
                    dbiList.append(DBInstanceBrief(
                        id=dbi['DBInstanceIdentifier'], engine=dbi['Engine'],
                        status='available', instance_class=dbi['DBInstanceClass'],
                        az=dbi['AvailabilityZone'],
                    ))
            return dbiList
        except ClientError as ex:
            raise ex

    def list_all_loadbalancer(self):
        from easyun.cloud.models import LoadBalancerDetail
        client = self._session.client('elbv2')
        try:
            elbs = client.describe_load_balancers()['LoadBalancers']
            return [
                LoadBalancerDetail(
                    id=elb['LoadBalancerName'], arn=elb['LoadBalancerArn'],
                    dns_name=elb['DNSName'], lb_type=elb['Type'],
                    state=elb['State']['Code'], scheme=elb['Scheme'],
                    ip_type=elb['IpAddressType'],
                    azs=[{'azName': az['ZoneName'], 'subnetId': az['SubnetId'], 'elbAddresses': az['LoadBalancerAddresses']} for az in elb.get('AvailabilityZones', [])],
                    security_groups=elb.get('SecurityGroups', []),
                    create_time=elb.get('CreatedTime'),
                )
                for elb in elbs
            ]
        except ClientError as ex:
            raise ex

    def get_loadbalancer_list(self):
        from easyun.cloud.models import LoadBalancerBrief
        client = self._session.client('elbv2')
        try:
            elbs = client.describe_load_balancers()['LoadBalancers']
            return [
                LoadBalancerBrief(
                    id=elb['LoadBalancerName'], arn=elb['LoadBalancerArn'],
                    dns_name=elb['DNSName'], lb_type=elb['Type'],
                    state=elb['State']['Code'], scheme=elb['Scheme'],
                )
                for elb in elbs
            ]
        except ClientError as ex:
            raise ex

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
