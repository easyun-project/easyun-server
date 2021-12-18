# -*- coding: utf-8 -*-
'''
@Description: The Server Management module
@LastEditors: 
'''
from apiflask import APIBlueprint
from easyun.common.models import Account, Datacenter

# define api version
ver = '/api/v1'

bp = APIBlueprint('服务器管理', __name__, url_prefix = ver+'/server') 

REGION = 'us-east-1'
VPC = 'vpc-057f0e3d715c24147'

# this_dc = Datacenter.query.first()
# REGION = this_dc.region
# FLAG = this_dc.name
# VPC = this_dc.vpc_id

from . import server_add, server_act, server_list, server_mod, server_parm, server_entity
