# -*- coding: utf-8 -*-
"""
  @module:  Subnet SDK Module
  @desc:    AWS SDK Boto3 Subnet Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from ..utils import get_easyun_session


class Subnet(object):
    def __init__(self, dc_name, sub_name):
        session = get_easyun_session(dc_name)
        self.dcName = dc_name
        self._resource = session.resource('ec2')
        self._client = self._resource.meta.client
        self.tagFilter = {'Name': 'tag:Flag', 'Values': [dc_name]}
