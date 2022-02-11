# -*- coding: utf-8 -*-
"""
  @module:  AWS Basic function
  @desc:    Contains some basic cloud functions
  @auth:    aleck
"""
import boto3
from ec2_metadata import ec2_metadata
from boto3.session import Session


def get_deploy_env(cloud):
    """获取后端服务器云环境基础信息"""
    if cloud == 'aws': 
        # 通过 sts接口获取 account_id
        try:
            client_sts = boto3.client('sts')
            account_id = client_sts.get_caller_identity().get('Account')
            # 通过 sts接口获取 iam_role
            role = client_sts.get_caller_identity().get('Arn').split('/')[1]
        except Exception:
            # 确保获取失败程序继续运行，下次重新获取
            account_id = 'missing'
            role = 'missing'

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

    

'''获取AWS Region 列表(区分海外和国内)'''
s = Session()
def get_aws_region(serviceName, account_type = 'Global'):
#     regions = 'us-east-1'
    try:
        if account_type == 'gcr':
            regionList = s.get_available_regions(serviceName, 'aws-cn')
        elif account_type == 'global':
            regionList = s.get_available_regions(serviceName)
        else:
            # regionList = 'account_type error'
            regionList = None
        return regionList
    except Exception as ex:
        return(ex)
#         return(ex.args)