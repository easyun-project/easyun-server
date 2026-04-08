# -*- coding: utf-8 -*-
"""
  @module:  Cloud Provider Entry
  @desc:    Multi-cloud entry point. Routes to provider based on Account/Datacenter data.
"""

from easyun.common.models import Account, Datacenter

# Provider registry — 新增 provider 时在这里注册
_PROVIDERS = {
    'aws': {
        'cloud_class': 'easyun.cloud.aws.AWSCloud',
        'datacenter_class': 'easyun.cloud.aws.datacenter.DataCenter',
        'account_class': 'easyun.cloud.aws.account.AWSAccount',
        'deploy_env_func': 'easyun.cloud.aws.get_aws_deploy_env',
    },
    # 'azure': {
    #     'cloud_class': 'easyun.cloud.azure.AzureCloud',
    #     'datacenter_class': 'easyun.cloud.azure.datacenter.DataCenter',
    #     'deploy_env_func': 'easyun.cloud.azure.get_azure_deploy_env',
    # },
}


def _import(dotted_path):
    """动态导入：'easyun.cloud.aws.AWSCloud' → AWSCloud 类"""
    module_path, attr_name = dotted_path.rsplit('.', 1)
    from importlib import import_module
    module = import_module(module_path)
    return getattr(module, attr_name)


def _get_provider_key(dc_name=None, account_id=None):
    """通过 datacenter 或 account 查询 provider 类型"""
    if dc_name:
        dc = Datacenter.query.filter_by(name=dc_name).first()
        if dc is None:
            raise ValueError(f'Datacenter {dc_name} not found')
        account_id = dc.account_id
    if account_id:
        account = Account.query.filter_by(account_id=account_id).first()
        if account is None:
            raise ValueError(f'Account {account_id} not found')
        return account.cloud.lower()
    raise ValueError('Either dc_name or account_id is required')


def get_datacenter(dc_name):
    """根据 datacenter 名称自动路由到对应 provider 的 DataCenter 实现"""
    provider = _get_provider_key(dc_name=dc_name)
    if provider not in _PROVIDERS:
        raise NotImplementedError(f'Provider {provider} not supported')
    cls = _import(_PROVIDERS[provider]['datacenter_class'])
    return cls(dc_name)


def get_cloud(account_id, region_type, provider=None):
    """获取 Cloud 实例，provider 自动从 account 推断或手动指定"""
    if provider is None:
        provider = _get_provider_key(account_id=account_id)
    if provider not in _PROVIDERS:
        raise NotImplementedError(f'Provider {provider} not supported')
    cls = _import(_PROVIDERS[provider]['cloud_class'])
    return cls(account_id, region_type)


def get_account(account_id=None, provider=None):
    """获取 CloudAccount 实例，用于 account 级别操作（quota/pricing/region）"""
    if provider is None:
        provider = _get_provider_key(account_id=account_id) if account_id else 'aws'
    if provider not in _PROVIDERS:
        raise NotImplementedError(f'Provider {provider} not supported')
    cls = _import(_PROVIDERS[provider]['account_class'])
    return cls(account_id)


def get_deploy_env(provider='aws'):
    """获取后端服务器云环境基础信息"""
    if provider not in _PROVIDERS:
        raise NotImplementedError(f'Provider {provider} not supported')
    func = _import(_PROVIDERS[provider]['deploy_env_func'])
    return func()


def create_datacenter(name, region, account_id, user=None, provider=None):
    """创建新的 DataCenter 逻辑容器"""
    if provider is None:
        account = Account.query.filter_by(account_id=account_id).first()
        provider = account.cloud.lower() if account else 'aws'
    if provider not in _PROVIDERS:
        raise NotImplementedError(f'Provider {provider} not supported')
    cls = _import(_PROVIDERS[provider]['datacenter_class'])
    return cls.create(name=name, region=region, account_id=account_id, user=user)
