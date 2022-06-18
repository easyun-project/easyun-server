# -*- coding: utf-8 -*-
"""
  @module:  Datacenter Resources SDK Module
  @desc:    AWS SDK Boto3 Resources Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from .sdk_server import EC2Server
from .sdk_volume import StorageVolume
from .sdk_bucket import StorageBucket
from .sdk_loadbalancer import LoadBalancer
from easyun.cloud.utils import get_easyun_session, get_server_name, get_subnet_type, get_eni_type, get_tag_name


_LOAD_BALANCER = None


def get_load_balancer(elb_id, dc_name):
    global _LOAD_BALANCER
    if _LOAD_BALANCER is not None and _LOAD_BALANCER.id == elb_id:
        return _LOAD_BALANCER
    else:
        return LoadBalancer(elb_id, dc_name)


class Resources(object):
    def __init__(self, dc_name):
        self.dcName = dc_name
        self.session = get_easyun_session(dc_name)
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dc_name]}
        self.flagTag = {'Key': 'Flag', "Value": dc_name}

    def list_all_volume(self):
        resource = self.session.resource('ec2')
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
                        diskType = 'system' if a['Device'] in SYSTEMDISK_PATH else 'user'
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
        resource = self.session.resource('ec2')
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
                    'createTime': vol.create_time
                }
                volumeList.append(volItem)
            return volumeList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_loadbalancer(self):
        client = self.session.client('elbv2')
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
                            'elbAddresses': i['LoadBalancerAddresses']
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
                    'createTime': elb['CreatedTime']
                }
                elbList.append(elbItem)
            return elbList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_loadbalancer_list(self):
        client = self.session.client('elbv2')
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
