# -*- coding: utf-8 -*-
'''
@Description: The Server Management module
@LastEditors: aleck
'''
from apiflask import APIBlueprint
from easyun.common.models import Account, Datacenter

# define api version
ver = '/api/v1'

bp = APIBlueprint('服务器管理', __name__, url_prefix = ver+'/server') 


# 单数据中心阶段预置参数
REGION = 'us-east-1'
thisDC = 'Easyun'
VPC = 'vpc-057f0e3d715c24147'

from . import server_add, server_act, server_get, server_mod, server_parm, server_entity