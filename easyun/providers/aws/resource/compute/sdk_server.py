# -*- coding: utf-8 -*-
"""
  @module:  Server (ec2) SDK Module
  @desc:    AWS SDK Boto3 EC2 Client and Resource Wrapper.
"""

from botocore.exceptions import ClientError
from ...session import get_easyun_session


# SDK: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance
from easyun.providers.base import ComputeInstanceBase

class EC2Server(ComputeInstanceBase):
    def __init__(self, svr_id, dc_name=None):
        self.id = svr_id
        session = get_easyun_session(dc_name)
        self._client = session.resource('ec2')
        self._resource = session.resource('ec2')
        try:
            self.svrObj = self._resource.Instance(self.id)
            self.tagName = next(
                (tag['Value'] for tag in self.svrObj.tags if tag["Key"] == 'Name'), None
            )
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_detail(self):
        '''get server's detail info'''
        try:
            pass
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, ex)

    def get_tags(self):
        try:
            return [t for t in self.svrObj.tags if t['Key'] not in ['Flag']]
        except Exception:
            return []

    def start(self):
        try:
            self.svrObj.start()
            return {'instanceId': self.id, 'action': 'start'}
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def stop(self):
        try:
            self.svrObj.stop()
            return {'instanceId': self.id, 'action': 'stop'}
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def reboot(self):
        try:
            self.svrObj.reboot()
            return {'instanceId': self.id, 'action': 'reboot'}
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def delete(self):
        try:
            self.svrObj.terminate()
            return {'instanceId': self.id, 'action': 'terminate'}
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
