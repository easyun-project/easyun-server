# -*- coding: utf-8 -*-
"""
  @module:  Dashboard
  @file:    dc_inventory.py
  @desc:    DataCenter resource inventory, including: server,storage,rds,networking,etc.
  @auth:    aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account

inventoryTable = {
    'summary' : 'easyun-inventory-summary',
    'server' : 'easyun-inventory-server',
    'stobject' : 'easyun-inventory-stobject',
    'stblock' : 'easyun-inventory-stblock',
    'rds' : 'easyun-inventory-rds',
    'subnet' : 'easyun-inventory-subnet',
    'gateway' : 'easyun-inventory-gateway'
}

deploy_region = "us-east-1"

@bp.get("/inventory/<dcName>/stblock")
@auth_required(auth_token)
# @output(SummaryOut)
def get_invty_stblock(dcName):
    '''获取 block storage 资源明细'''
    try:
        resource_ddb = boto3.resource('dynamodb', region_name= deploy_region)    
        table = resource_ddb.Table('easyun-inventory-block')
        diskInvty = table.get_item(
            Key={'dcName': dcName}
        )['Item']['diskInventory']

        resp = Result(detail = diskInvty, status_code=200)
        return resp.make_resp()

    except Exception as e:
        resp = Result(
            message=str(e), 
            status_code=7010
        )
        return resp.err_resp()  