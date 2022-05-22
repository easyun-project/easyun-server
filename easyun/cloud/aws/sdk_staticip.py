# -*- coding: utf-8 -*-
"""
  @module:  Static IP SDK Module
  @desc:    AWS SDK Boto3 StaticIP(EIP) Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from ..utils import get_easyun_session


class StaticIP(object):
    def __init__(self, dc_name, ip_add=None):
        session = get_easyun_session(dc_name)
        self.dcName = dc_name
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dc_name]}
