# -*- coding: utf-8 -*-
"""
  @module:  Subnet SDK Module
  @desc:    AWS SDK Boto3 Subnet Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from easyun.libs.utils import len_iter
from ..session import get_easyun_session


class Subnet(object):
    def __init__(self, sub_id, dc_name=None):
        session = get_easyun_session(dc_name)
        self.id = sub_id
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        try:
            self.subnetObj = self._resource.Subnet(self.id)
            self.cidrBlock = self.subnetObj.cidr_block
            self.tagName = next(
                (tag['Value'] for tag in self.subnetObj.tags if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_server_numb(self):
        # 统计subnet下的服务器数量
        svrCollection = self.subnetObj.instances.all()
        return len_iter(svrCollection)

    def get_eni_numb(self):
        # 统计subnet下的网卡数量
        eniCollection = self.subnetObj.network_interfaces.all()
        return len_iter(eniCollection)

    def get_subnet_type(self):
        '''判断subnet type是 public 还是 private'''
        # 偷个懒仅以名称判断，完整功能待实现
        lowerName = self.tagName.lower()
        try:
            if lowerName.startswith('pub'):
                subnetType = 'public'
            elif lowerName.startswith('pri'):
                subnetType = 'private'
            else:
                subnetType = 'unknown'
            return subnetType
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        subnet = self.subnetObj
        try:
            userTags = [t for t in subnet.tags if t['Key'] not in ['Flag', 'Name']]
            subnetDetail = {
                'subnetId': self.id,
                'subnetState': subnet.state,
                'subnetType': self.get_subnet_type(),
                'cidrBlock': subnet.cidr_block,
                'azName': subnet.availability_zone,
                'vpcId': subnet.vpc_id,
                'tagName': self.tagName,  
                'availableIpNum': subnet.available_ip_address_count,
                'isMapPublicIp': subnet.map_public_ip_on_launch,
                'serverNum': self.get_server_numb(),
                'eniNum': self.get_server_numb(),
                'userTags': userTags
            }
            return subnetDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        subnet = self.subnetObj
        svrNum = self.get_server_numb()
        try:
            if svrNum == 0 and self.get_eni_numb == 0:
                subnet.delete()
            else:
                raise ValueError(f'Subnet NOT Empty, contains {svrNum} Server(s) resources.')
            oprtRes = {
                'operation': 'Delete Subnet',
                'subnetId': self.id,
                'tagName': self.tagName,
            }
            # del self
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
