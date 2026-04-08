# -*- coding: utf-8 -*-
'''
@Description: The Dashboard module
@LastEditors: 
'''
from apiflask import APIBlueprint
from easyun.cloud import get_deploy_env


# define api version
ver = '/api/v1'

# 获取Easyun部署region信息
# DeployRegion = get_deploy_env('aws').get('deploy_region'),
# 指定为开发测试环境region
DeployRegion = 'us-east-1'

bp = APIBlueprint('监控面板', __name__, url_prefix=ver + '/dashboard')

from . import api_inventory, api_summary, api_mock
