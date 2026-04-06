# -*- coding: utf-8 -*-
"""
  @module:  AWS Account
  @desc:    AWS account-level operations (quota, pricing, regions)
"""

from easyun.providers.base import CloudAccountBase
from .session import get_easyun_session


class AWSAccount(CloudAccountBase):
    def __init__(self, account_id=None):
        self.account_id = account_id
        self._session = get_easyun_session()

    def list_regions(self):
        from .region import AWS_Regions
        return AWS_Regions

    def get_quota(self, service_code, quota_code, region=None):
        from .management.sdk_quotas import ServiceQuotas
        sq = ServiceQuotas(region)
        return sq.get_service_quota(service_code, quota_code)

    def get_quotas(self, service_code, quota_codes, region=None):
        from .management.sdk_quotas import ServiceQuotas
        sq = ServiceQuotas(region)
        return sq.get_service_quotas(service_code, quota_codes)

    def get_pricing(self, service_code, **kwargs):
        from .management.sdk_pricing import AwsPricing
        return AwsPricing()
