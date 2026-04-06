# -*- coding: utf-8 -*-
"""
  @module:  Dashboard Summary
  @desc:    DataCenter summary info
"""

from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.models import Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.libs.utils import filter_list_by_key
from easyun.providers import get_datacenter
from .api_inventory import query_inventory
from .schemas import AzSummaryItem, HealthSummaryOut, ResourceSumItem
from . import bp


@bp.get("/summary/datacenter")
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(AzSummaryItem(many=True))
def summary_dc(parm):
    '''获取数据中心 Summary信息'''
    dc = get_datacenter(parm['dc'])
    summaryList = dc.get_az_summary()
    resp = Result(detail=summaryList)
    return resp.make_resp()


@bp.get("/summary/health")
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(HealthSummaryOut)
def summary_health(parm):
    '''获取健康状态 Summary信息'''
    try:
        dc = get_datacenter(parm['dc'])
        alarms = dc.get_cloudwatch_alarms()
        dashboards = dc.get_cloudwatch_dashboards()
        summary_list = {"alarms": alarms, "dashboards": dashboards}
        resp = Result(detail=summary_list)
        return resp.make_resp()
    except Exception as e:
        resp = Result(detail=str(e), status_code=7010)
        return resp.err_resp()


@bp.get("/summary/resource")
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(ResourceSumItem(many=True))
def summary_resource(parm):
    '''获取所有IaaS资源 Summary信息'''
    dcName = parm['dc']

    serverList = query_inventory('server', dcName).get('data')
    stateList = filter_list_by_key(serverList, 'svrState')
    vcpuList = filter_list_by_key(serverList, 'vpuNum')
    ramList = filter_list_by_key(serverList, 'ramSize')
    serverSum = {
        "type": "server",
        'data': {
            "sumNum": len(serverList),
            "runNum": stateList.count('running'),
            "stopNum": stateList.count('stopped'),
            "vcpuNum": sum([int(i) for i in vcpuList]),
            "ramSize": {'value': sum([float(i) for i in ramList]), 'unit': 'GiB'},
        },
    }

    databaseList = query_inventory('database', dcName).get('data')
    engineList = filter_list_by_key(databaseList, 'dbiEngine')
    databaseSum = {
        "type": "database",
        "data": {
            "sumNum": len(databaseList),
            "auroraNum": engineList.count('aurora-mysql'),
            "mysqlNum": engineList.count('mysql'),
            "mariadbNum": engineList.count('mariadb'),
            "postgresNum": engineList.count('postgres'),
        },
    }

    volumeList = query_inventory('volume', dcName).get('data')
    volumeSum = {
        "type": "volume",
        "data": {
            "sumNum": len(volumeList),
        },
    }

    bucketList = query_inventory('bucket', dcName).get('data')
    bucketSum = {
        "type": "bucket",
        "data": {
            "sumNum": len(bucketList),
        },
    }

    elbList = query_inventory('elb', dcName).get('data')
    elbSum = {
        "type": "elb",
        "data": {
            "sumNum": len(elbList),
        },
    }

    summaryList = [serverSum, databaseSum, volumeSum, bucketSum, elbSum]
    resp = Result(detail=summaryList)
    return resp.make_resp()
