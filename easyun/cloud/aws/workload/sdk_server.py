# -*- coding: utf-8 -*-
"""
  @module:  Server (ec2) SDK Module
  @desc:    AWS SDK Boto3 EC2 Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from ..session import get_easyun_session


# SDK: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance
class EC2Server(object):
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
