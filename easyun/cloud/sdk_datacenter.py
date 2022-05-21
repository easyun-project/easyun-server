# -*- coding: utf-8 -*-
"""
  @module:  Datacenter SDK Module
  @desc:    AWS SDK Boto3 VPC Client and Resource Wrapper.
  @auth:    aleck
"""

from botocore.exceptions import ClientError
from .utils import get_easyun_session


class DataCenter(object):
    def __init__(self, dcName):
        session = get_easyun_session(dcName)
        self.dcName = dcName
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dcName]}

    def get_azone_list(self):
        try:
            azs = self._client.describe_availability_zones()
            azoneList = [az['ZoneName'] for az in azs['AvailabilityZones']]
            return azoneList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def list_all_secgroup(self):
        try:
            secGroups = self._client.describe_security_groups(Filters=[self.tagFilter])[
                'SecurityGroups'
            ]

            secgroupList = []
            for sg in secGroups:
                # 获取Tag:Name
                nameTag = next(
                    (tag['Value'] for tag in sg.get('Tags') if tag["Key"] == 'Name'),
                    None,
                )
                sgItem = {
                    'sgId': sg['GroupId'],
                    'tagName': nameTag,
                    'sgName': sg['GroupName'],
                    'sgDes': sg['Description'],
                    # Inbound Ip Permissions
                    'ibrulesNum': len(sg['IpPermissions']),
                    'ibPermissions': sg['IpPermissions'],
                    # Outbound Ip Permissions
                    'obrulesNum': len(sg['IpPermissionsEgress']),
                    'obPermissions': sg['IpPermissionsEgress'],
                }
                secgroupList.append(sgItem)
            return secgroupList
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_secgroup_list(self):
        try:
            return self.list_all_secgroup()
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
