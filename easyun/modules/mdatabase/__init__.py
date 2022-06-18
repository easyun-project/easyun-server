# -*- coding: utf-8 -*-
"""The Storage management module."""
from apiflask import APIBlueprint
from easyun import log
from easyun.common.models import Account, Datacenter

# define api version
ver = '/api/v1'

bp = APIBlueprint('数据库管理', __name__, url_prefix=ver + '/database')

logger = log.create_logger('mdb')

from . import api_database_get, aip_mock
