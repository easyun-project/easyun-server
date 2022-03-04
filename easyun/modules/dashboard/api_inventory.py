# -*- coding: utf-8 -*-
"""
  @module:  Dashboard Inventory
  @desc:    DataCenter resource inventory, including: server,storage,rds,networking,etc.
  @auth:    aleck
"""

import boto3
from apiflask import auth_required, Schema
from apiflask.fields import String, List, Nested, Boolean, Date
from apiflask.validators import Length, OneOf
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from . import bp, DeployRegion


# 定义各资源的表格名称
RESOURCE_NAME = [
    'all',  # 一次性获取全部资源清单
    'server',  # 服务器(EC2)
    'database',  # 数据库(RDS)
    'st_block',  # 块存储(EBS)
    'st_object',  # 对象存储(S3)
    'st_files',  # 文件存储(EFS,FSx)
    'nw_subnet',  # 子网(Subnet)
    'nw_secgroup',  # 安全组(SecurityGroup)
    'nw_gateway',  # 网关(IGW，NatGW)
]

# 定义各资源对应的ddb表名称
INVENTORY_TABLE = {
    'server': 'easyun-inventory-server',
    'database': 'easyun-inventory-database',
    'st_block': 'easyun-inventory-stblock',
    'st_object': 'easyun-inventory-stobject',
    'st_files': 'easyun-inventory-stfiles',
    'nw_subnet': 'easyun-inventory-subnet',
    'nw_secgroup': 'easyun-inventory-secgroup',
    'nw_gateway': 'easyun-inventory-gateway'
}


@bp.get("/inventory/<resource>")
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def get_inventory(resource, parm):
    '''获取数据中心资源明细(Inventory)'''
    if resource not in RESOURCE_NAME:
        resp = Result(
            detail='Unknown input resource. The supported resource are:' + str(RESOURCE_NAME),
            message='Validation error',
            status_code=7001,
            http_status_code=400
        )
        return resp.err_resp()
    #获取查询参数 ?dc=xxx ,默认值‘Easyun’
    dcName = parm.get('dc')
    try:
        # thisDC = Datacenter.query.filter_by(name=dcName).first()
        # dcRegion = thisDC.get_region()
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = DeployRegion)

        inventoryList = [
            query_inventory('server', dcName),
            query_inventory('st_object', dcName),
            query_inventory('st_block', dcName),
            query_inventory('st_files', dcName),
            query_inventory('database', dcName),
            query_inventory('nw_subnet', dcName),
            query_inventory('nw_secgroup', dcName),
            query_inventory('nw_gateway', dcName)
        ]

        if resource == 'all':
            invtList = inventoryList

        else:
            for i in inventoryList:
                if i.get('type') == resource:
                    invtList = i.get('data')

        resp = Result(
            detail=invtList
        )
        return resp.make_resp()

    except Exception as e:
        resp = Result(
            detail=str(e),
            status_code=7010
        )
        return resp.err_resp()


# 从INVENTORY_TABLE字典中匹配资源对应的表名
def get_tabname(resource):
    return INVENTORY_TABLE.get(resource)


def query_inventory(resource, dcName):
    '''Query inventory from Dynamodb table'''
    try:
        resource_ddb = boto3.resource('dynamodb')
        table = resource_ddb.Table(get_tabname(resource))
        inventory = table.get_item(
            Key={'dcName': dcName}
        )['Item']['dcInventory']
        return {
            'type': resource,
            'data': inventory
        }

    except Exception as ex:
        return {
            'type': resource,
            'data': [],
            'msg': str(ex)
        }
