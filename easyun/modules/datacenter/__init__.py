# -*- coding: utf-8 -*-
"""
  @file:    __init__.py
  @desc:    DataCenter API Init module
"""

from apiflask import APIBlueprint
from easyun import log
from easyun.cloud.aws import SecurityGroup, Subnet, StaticIP


# define api version
ver = '/api/v1'

bp = APIBlueprint('数据中心管理', __name__, url_prefix=ver + '/datacenter')
logger = log.create_logger('dcm')

# 单数据中心模式下，名称默认：Easyun
# DC_NAME = "Easyun"
# 单数据中心模式下，DC Region 同 Deployed Region
# DC_REGION = 'us-east-1'
# REGION = 'us-east-1'
# VERBOSE = 1
DryRun = False


from . import (
    api_datacenter_get,
    api_datacenter_mgt,
    api_datacenter_sum,
    api_subnet_mgt,
    api_routetab_mgt,
    api_secgroup_mgt,
    api_staticip_mgt,
    api_gateway_mgt
)

bp.register_blueprint(api_subnet_mgt.bp)
bp.register_blueprint(api_routetab_mgt.bp)
bp.register_blueprint(api_gateway_mgt.bp)
bp.register_blueprint(api_secgroup_mgt.bp)
bp.register_blueprint(api_staticip_mgt.bp)
