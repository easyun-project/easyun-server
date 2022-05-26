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
from easyun.cloud.utils import get_easyun_session, get_server_name, get_subnet_type, get_eni_type, get_tag_name


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
                    if vol.multi_attach_enabled or vol['State'] == 'available'
                    else False
                )
                volItem = {
                    'volumeId': vol.id,
                    'tagName': nameTag,
                    'volumeAz': vol.availability_zone,
                    'volumeType': vol.volume_type,
                    'volumeSize': vol.size,
                    'volumeState': vol.state,
                    'isAttachable': isAttachable,
                    'createTime': vol.create_time,
                    'isEncrypted': vol.encrypted,
                    'isMultiAttach': vol.multi_attach_enabled,
                    #             'usedSize': none,
                    'volumeIops': vol.iops,
                    'volumeThruput': vol.throughput,
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
                    if vol['MultiAttachEnabled'] or vol['State'] == 'available'
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

