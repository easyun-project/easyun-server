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

    # --- KeyPair 管理（region 级别）---

    def list_keypairs(self, region=None, dc_name=None):
        """列出指定 region 下的 keypair"""
        from easyun.providers.models import KeyPairInfo
        session = get_easyun_session(dc_name)
        client = session.client('ec2', region_name=region)
        filters = [{'Name': 'tag:Flag', 'Values': [dc_name]}] if dc_name else []
        keys = client.describe_key_pairs(Filters=filters).get('KeyPairs', [])
        return [
            KeyPairInfo(
                name=k['KeyName'], key_type=k['KeyType'],
                fingerprint=k['KeyFingerprint'],
                tags=[t for t in k.get('Tags', []) if t['Key'] != 'Flag'],
            )
            for k in keys
        ]

    def get_keypair(self, key_name, region=None):
        from easyun.providers.models import KeyPairInfo
        session = get_easyun_session()
        resource = session.resource('ec2', region_name=region)
        kp = resource.KeyPair(key_name)
        return KeyPairInfo(
            name=key_name, key_type=kp.key_type,
            fingerprint=kp.key_fingerprint,
            tags=[t for t in (kp.tags or []) if t['Key'] != 'Flag'],
        )

    def create_keypair(self, key_name, key_type='rsa', region=None, dc_name=None):
        """创建 keypair，返回 (KeyPairInfo, key_material)"""
        from easyun.providers.models import KeyPairInfo
        session = get_easyun_session()
        resource = session.resource('ec2', region_name=region)
        tags = [{'Key': 'Flag', 'Value': dc_name}] if dc_name else []
        kp = resource.create_key_pair(
            KeyName=key_name, KeyType=key_type,
            TagSpecifications=[{'ResourceType': 'key-pair', 'Tags': tags}] if tags else [],
        )
        info = KeyPairInfo(name=key_name, key_type=key_type, fingerprint=kp.key_fingerprint)
        return info, kp.key_material

    def delete_keypair(self, key_name, region=None):
        session = get_easyun_session()
        client = session.client('ec2', region_name=region)
        client.delete_key_pair(KeyName=key_name)
