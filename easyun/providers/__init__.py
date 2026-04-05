# -*- coding: utf-8 -*-
"""
  @module:  Cloud Provider Entry
  @desc:    Multi-cloud entry point. Currently supports AWS only.
  @auth:    aleck
"""
from .aws import AWSCloud


def get_cloud(account_id, region_type, provider='aws'):
    if provider == 'aws':
        return AWSCloud(account_id, region_type)
    else:
        raise NotImplementedError(f'Provider {provider} not supported yet')


def get_deploy_env(provider='aws'):
    """获取后端服务器云环境基础信息，按 provider 分发"""
    if provider == 'aws':
        from .aws import get_aws_deploy_env
        return get_aws_deploy_env()
    else:
        raise NotImplementedError(f'Provider {provider} not supported yet')
