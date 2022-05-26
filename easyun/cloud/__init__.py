# -*- coding: utf-8 -*-
"""
  @module:  AWS Basic function
  @desc:    Contains some basic cloud functions
  @auth:    aleck
"""
import boto3
from ec2_metadata import ec2_metadata
from boto3.session import Session
from .aws import AWSCloud


_AWS_CLOUD = None


def get_aws_cloud(account_id, region_type):
    global _AWS_CLOUD
    if _AWS_CLOUD is not None and _AWS_CLOUD.account_id == account_id:
        return _AWS_CLOUD
    else:
        return AWSCloud(account_id, region_type)


def get_deploy_env(provider='aws'):
    """获取后端服务器云环境基础信息"""
    if provider == 'aws':
        # 通过 sts接口获取 account_id
        try:
            client_sts = boto3.client('sts')
            # 通过 sts接口获取 account id
            account_id = client_sts.get_caller_identity().get('Account')
            # 通过 sts接口获取 iam_role
            role = client_sts.get_caller_identity().get('Arn').split('/')[1]
        except Exception:
            # 确保获取失败程序继续运行，下次重新获取
            account_id = 'unknow'
            role = 'undefined'

        # 获取 deploy region
        try:
            # 从ec2 metadata 获取 region 信息
            deploy_region = ec2_metadata.region
        except Exception:
            # 如果获取失败则获取本地配置信息 (需在 aws configure 设置默认region)
            deploy_region = boto3.session.Session().region_name

        # Define AWS China Region list
        GCR_REGION_LIST = ['cn-north-1', 'cn-northwest-1']
        # 判断 account_type
        if deploy_region in GCR_REGION_LIST:
            region_type = 'GCR'
        else:
            region_type = 'Global'

        # cloud = get_aws_cloud(account_id, region_type)

    else:
        # 匹配部署在其它云环境的获取方法(待实现)
        pass

    return {
        'accountId': account_id,
        'role': role,
        'deployRegion': deploy_region,
        'regionType': region_type,
    }
