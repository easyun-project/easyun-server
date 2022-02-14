# -*- coding: utf-8 -*-
"""
  @module:  Dashboard Mock API
  @desc:    put dashboard module's mock api code here.
  @auth:    
"""

from apiflask import Schema, input, output, auth_required
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.schemas import DcNameQuery



@bp.get("/summary/resource")
@auth_required(auth_token)
@input(DcNameQuery, location='query')
@auth_required(auth_token)
def graph_summary(parm):
    '''获取 IaaS资源 Summary信息[Mock]'''
    dcName = parm['dc']
    summaryList = [
        {
            "type":"server",
            'data':{
                "sumNum": 19,
                "runNum": 15,
                "stopNum": 4,
                "vcpuNum": 76,
                "ramSize": {
                    'value':119,
                    'unit':'GiB'
                }
            }
        },
        {
            "type":"database",
            "data":{
                "sumNum": 7,
                "mysqlNum": 3,
                "mariaNum": 2,
                "postgreNum": 1,
                "auroraNum": 0,
                "cacheNum": 1
            }
        },
        {
            "type":"network",
            "data":{
                "sumNum": 4,
                "pubNum": 2,
                "priNum": 2,
                "igwNum": 1,
                "natNum": 1,
                "sgNum": 3
            }
        },
        {
            "type":"st_object",
            "data":{
                "sumNum": 6,
                "objSize": {
                    'value':17.1,
                    'unit':'GiB'
                },
                "objNum": 502013,
                "pubNum": 1,
                "encNum": 5
            }
        },
        {
            "type":"st_block",
            "data":{
                "sumNum": 12,
                "blcSize": {
                    'value': 20.52,
                    'unit':'TiB'
                },
                "useNum": 10,
                "avlNum": 2,
                "encNum": 3
            }
        },
        {
            "type":"st_file",
            "data":{
                "sumNum": 3,
                "efsNum": 1,
                "efsSize": {
                    'value': 827.7,
                    'unit':'MiB'
                },
                "fsxNum": 2,
                "fsxSize": {
                    'value': 3.27,
                    'unit':'GiB'
                }
            }
        }
    ]

    resp = Result(
        detail = summaryList
        )
    return resp.make_resp()




'''数据中心资源明细(Inventory) [Mock]'''

serverList = [
    {
        "priIp": "10.10.1.153",
        "svrId": "i-09aa9e2c83d840ab1",
        "volumeSize": 24,
        "pubIp": "34.207.216.18",
        "svrState": "stopped",
        "azName": "us-east-1a",
        "insType": "t4g.nano",
        "vpuNum": 2,
        "osName": "Linux/UNIX",
        "ramSize": 0.5,
        "tagName": "test-devbk",
        "createTime": "2021-11-06T09:10:41.173000+00:00"
    },
    {
        "priIp": "10.10.1.32",
        "svrId": "i-043e8074448089cad",
        "volumeSize": 28,
        "pubIp": "54.224.217.126",
        "svrState": "stopped",
        "azName": "us-east-1a",
        "insType": "t4g.nano",
        "vpuNum": 2,
        "osName": "Linux/UNIX",
        "ramSize": 0.5,
        "tagName": "test-notebook-svr",
        "createTime": "2021-12-09T09:10:41.173000+00:00"
    },
    {
        "priIp": "10.10.1.39",
        "svrId": "i-0199109e87f5fc8bd",
        "volumeSize": 29,
        "pubIp": "34.207.216.182",
        "svrState": "running",
        "azName": "us-east-1a",
        "insType": "t4g.nano",
        "vpuNum": 2,
        "osName": "Linux/UNIX",
        "ramSize": 0.5,
        "tagName": "boto3test",
        "createTime": "2021-12-19T09:10:41.173000+00:00"
    },
    {
        "priIp": "10.10.1.214",
        "svrId": "i-01bf31db382e24093",
        "volumeSize": 29,
        "pubIp": "34.207.216.181",
        "svrState": "stopped",
        "azName": "us-east-1a",
        "insType": "t4g.nano",
        "vpuNum": 2,
        "osName": "Linux/UNIX",
        "ramSize": 0.5,
        "tagName": "test-from-dev",
        "createTime": "2021-11-09T09:10:41.173000+00:00"
    }
]


st_objectList = {
    "type":"st_object",
    "data":[
        {
        "bktName": "bktexample17",
        "bktRegion": "us-east-1",
        "bktStatus": "Objects can be public"
        },
        {
        "bktName": "easyun-api-test-13",
        "bktRegion": "us-east-1",
        "bktStatus": "Objects can be public"
        },
        {
        "bktName": "easyun-api-test-11",
        "bktRegion": "us-east-1",
        "bktStatus": "Objects can be public"
        },
        {
        "bktName": "easyun-api-test-12",
        "bktRegion": "us-east-1",
        "bktStatus": "Objects can be public"
        }
    ]
}

st_fileList = {
    "type":"st_file",
    "data":[
    ]
}

databaseList = {
    "type":"database",
    "data":[
    ]
}

nw_subnetList = {
    "type":"nw_subnet",
    "data":[
    ]
}

nw_secgroupList = {
    "type":"nw_secgroup",
    "data":[
    ]
}

nw_gatewayList = {
    "type":"nw_gateway",
    "data":[
    ]
}