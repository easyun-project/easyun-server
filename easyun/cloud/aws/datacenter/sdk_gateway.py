# -*- coding: utf-8 -*-
"""
  @module:  Static IP SDK Module
  @desc:    AWS SDK Boto3 StaticIP(EIP) Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from ..session import get_easyun_session


class InternetGateway(object):
    def __init__(self, igw_id, dc_name=None):
        session = get_easyun_session(dc_name)
        self.id = igw_id
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        try:
            self.igwObj = self._resource.InternetGateway(self.id)
            self.tagName = next(
                (tag['Value'] for tag in self.igwObj.tags if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        igw = self.igwObj
        try:
            userTags = [t for t in igw.tags if t['Key'] not in ['Flag', 'Name']]
            # 暂时只考虑1个igw对应1个vpc情况
            igwAttach = igw.attachments[0]
            igwDetail = {
                'igwId': igw.id,
                'tagName': self.tagName,
                'vpcId': igwAttach['VpcId'],
                'state': igwAttach['State'],
                # 'dcName': dcName,
                'userTags': userTags
            }
            return igwDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        igw = self.igwObj
        try:
            vpcId = igw.attachments[0].get('VpcId')
            igw.detach_from_vpc(vpcId)
            igw.delete()
            oprtRes = {
                'operation': 'Delete Internet Gateway',
                'igwId': self.id,
                'tagName': self.tagName,
            }
            # del self
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))


class NatGateway(object):
    def __init__(self, natgw_id, dc_name=None):
        session = get_easyun_session(dc_name)
        self.id = natgw_id
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        try:
            self.natgwDict = self._client.describe_nat_gateways(
                NatGatewayIds=[natgw_id]
            )['NatGateways'][0]
            self.tagName = next(
                (tag['Value'] for tag in self.natgwDict['Tags'] if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        nat = self.natgwDict
        try:
            userTags = [t for t in nat['Tags'] if t['Key'] not in ['Flag', 'Name']]
            # 暂时只考虑1个natgw对应1个ip情况
            natAddr = nat['NatGatewayAddresses'][0]
            natDetail = {
                'natgwId': nat['NatGatewayId'],
                'tagName': self.tagName,
                'subnetId': nat['SubnetId'],
                'vpcId': nat['VpcId'],
                # 'dcName': dcName,
                'state': nat['State'],
                'createTime': nat['CreateTime'],
                'connectType': nat['ConnectivityType'],
                'network': {
                    'publicIp': natAddr['PublicIp'],
                    'allocationId': natAddr['AllocationId'],
                    'privateIp': natAddr['PrivateIp'],
                    'eniId': natAddr['NetworkInterfaceId']
                },
                'userTags': userTags,
            }
            return natDetail
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        nat = self.natgwDict
        try:
            if nat['State'] != 'deleted':
                self._client.delete_nat_gateway(
                    NatGatewayId=self.id
                )
            else:
                raise ValueError('The NAT Gateway was deleted!')
            oprtRes = {
                'operation': 'Delete NAT Gateway',
                'natgwId': self.id,
                'tagName': self.tagName,
            }
            # del self
            return oprtRes
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
