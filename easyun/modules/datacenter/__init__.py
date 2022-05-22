# -*- coding: utf-8 -*-
"""
  @file:    _init_.py
  @desc:    DataCenter Init module
"""

from apiflask import APIBlueprint
from easyun import log
from easyun.cloud.aws import DataCenter, SecurityGroup, Subnet, StaticIP


# define api version
ver = '/api/v1'

bp = APIBlueprint('数据中心管理', __name__, url_prefix=ver + '/datacenter')
logger = log.create_logger('dcm')

# 单数据中心模式下，名称默认：Easyun
DC_NAME = "Easyun"
# 单数据中心模式下，DC Region 同 Deployed Region
DC_REGION = 'us-east-1'
REGION = 'us-east-1'
VERBOSE = 1
DryRun = False


_DATA_CENTER = None
_SEC_GROUP = None
_SUB_NET = None


def get_datacenter(dc_name):
    global _DATA_CENTER
    if _DATA_CENTER is not None and _DATA_CENTER.dcName == dc_name:
        return _DATA_CENTER
    else:
        return DataCenter(dc_name)


def get_sub_net(dc_name):
    global _SUB_NET
    if _SUB_NET is not None and _SUB_NET.dcName == dc_name:
        return _SUB_NET
    else:
        return SecurityGroup(dc_name)


def get_secgroup(sg_id, dc_name):
    global _SEC_GROUP
    if _SEC_GROUP is not None and _SEC_GROUP.sgId == sg_id:
        return _SEC_GROUP
    else:
        return SecurityGroup(sg_id, dc_name)


from . import (
    api_datacenter_get,
    api_datacenter_mgt,
    api_datacenter_sum,
    api_subnet_mgt,
    api_secgroup_mgt,
    api_staticip_mgt,
    api_gateway_mgt,
    api_routetab_mgt
)
