# -*- coding: utf-8 -*-
"""
  @module:  Dashboard Inventory
  @desc:    DataCenter resource inventory, including: server,storage,rds,networking,etc.
  @auth:    
"""

import boto3
from apiflask import Schema, input, output, auth_required
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter


SUMMARY_TABLE = {
    'summary' : 'easyun-inventory-summary',
}