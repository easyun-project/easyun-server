# -*- coding: utf-8 -*-
"""
  @file:    _init_.py
  @desc:    DataCenter Init module
"""

from apiflask import APIBlueprint
from easyun import log

# define api version
ver = '/api/v1'

bp = APIBlueprint('数据中心管理', __name__, url_prefix=ver + '/datacenter')

# 单数据中心模式下，名称默认：Easyun
# tag:FLAG = DC_NAME,
DC_NAME = "Easyun"
# 单数据中心模式下，DC Region 同 Deployed Region
DC_REGION = 'us-east-1'
REGION = 'us-east-1'
# this_account = Account.query.filter_by(id=1).first()
# DC_REGION = this_account.get_region()


VERBOSE = 1
DryRun = False

logger = log.create_logger('dcm')


from . import (
    api_datacenter_get,
    api_datacenter_mgt,
    api_datacenter_sum,
    dcm_secgroup,
    dcm_staticip,
    dcm_subnet,
)
