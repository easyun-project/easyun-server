# -*- coding: utf-8 -*-
"""The Load Banalancer Management Module."""
from apiflask import APIBlueprint
from easyun import log
from easyun.common.models import Account, Datacenter

# define api version
ver = '/api/v1'

bp = APIBlueprint('负载均衡器管理', __name__, url_prefix=ver + '/loadbalancer')

logger = log.create_logger('melb')

from . import api_loadbalancer_get
