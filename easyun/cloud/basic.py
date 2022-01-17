# -*- coding: utf-8 -*-
"""
  @module:  Basic function
  @desc:    Contains some basic cloud functions
  @auth:    aleck
"""
import boto3
from ec2_metadata import ec2_metadata


def get_deploy_env(cloud):
    """获取后端服务器部署的云环境基础信息"""
    if cloud == 'aws': 
        # 通过 sts接口获取 account_id
        client_sts = boto3.client('sts')
        account_id = client_sts.get_caller_identity().get('Account')
        # 通过 sts接口获取 iam_role
        role = client_sts.get_caller_identity().get('Arn').split('/')[1]

        # 获取 deploy region  
        try:
            # 从ec2 metadata 获取 region 信息
            deploy_region = ec2_metadata.region
        except Exception:
            # 如果获取失败则获取本地配置信息 (需在 aws configure 设置默认region)
            deploy_region = boto3.session.Session().region_name

        # 判断 account_type
        gcr_regions = ['cn-north-1', 'cn-northwest-1']
        if deploy_region in gcr_regions:
            aws_type = 'GCR'
        else:
            aws_type = 'Global'
    
    else:
        # 匹配部署在其它云环境的获取方法(待实现)  
        pass
    
    return {
        'account_id': account_id,
        'role': role,
       'deploy_region': deploy_region,        
        'aws_type' : aws_type
    }

    
