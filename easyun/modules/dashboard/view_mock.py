# -*- coding: utf-8 -*-
"""dashboard model views."""

from apiflask import Schema, input, output, auth_required
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account


class QueryIn(Schema):
    dc = String(required=True, example='Easyun')

@bp.get("/summary/datacenter")
@auth_required(auth_token)
@input(QueryIn, location='query')
def summary_dc(parm):
    '''获取 数据中心 Summary信息[Mock]'''
    dcName = parm['dc']
    summaryList = [
      {
        "azName": "us-east-1a",
        "dcRegion": {
            "icon":"USA",
            "name":"US East (N. Virginia)",            
        },
        "azStatus": "running",
        "subnetNum": 2
      },
      {
        "azName": "us-east-1b",
        "dcRegion": {
            "icon":"USA",
            "name":"US East (N. Virginia)",            
        },
        "azStatus": "running",
        "subnetNum": 2
      },
      {
        "azName": "us-east-1c",
        "dcRegion": {
            "icon":"USA",
            "name":"US East (N. Virginia)",            
        },
        "azStatus": "empty",
        "subnetNum": 0
      },
      {
        "azName": "us-east-1d",
        "dcRegion": {
            "icon":"USA",
            "name":"US East (N. Virginia)",            
        },
        "azStatus": "empty",
        "subnetNum": 0
      },
      {
        "azName": "us-east-1e",
        "dcRegion": {
            "icon":"USA",
            "name":"US East (N. Virginia)",            
        },
        "azStatus": "running",
        "subnetNum": 1
      }
    ]

    resp = Result(
        detail = summaryList
        )
    return resp.make_resp()   


@bp.get("/summary/health")
@auth_required(auth_token)
@input(QueryIn, location='query')
def summary_health(parm):
    '''获取 健康状态 Summary信息[Mock]'''
    dcName = parm['dc'] 
    summaryList = {
        "alarms": {
            "iaNum": 1,
            "isNum": 3,
            "okNum": 2
        },
        "dashboards": [
            {
                'title' : 'Easyun Overview',
                'url': 'http://www.aws-cloudwatch.com/xxxx'
            },
            {
                'title' : 'EC2 Dashboard',
                'url': 'http://www.aws-cloudwatch.com/xxxx'
            },
            {         
                'title' : 'RDS Dashobard',
                'url': 'http://www.aws-cloudwatch.com/xxxx'
            },
            {
                'title' : 'Storage',
                'url': 'http://www.aws-cloudwatch.com/xxxx'
            }
        ]
    }

    resp = Result(
        detail = summaryList
        )
    return resp.make_resp()


@bp.get("/summary/resource")
@auth_required(auth_token)
@input(QueryIn, location='query')
@auth_required(auth_token)
def graph_summary(parm):
    '''获取 IaaS资源 Summary信息[Mock]'''
    dcName = parm['dc']
    summaryList = [
        {
            "type":"server",
            'data':{
                "total": 19,
                "runNum": 15,
                "stopNum": 4,
                "vcpuNum": 76,
                "ramSize": 119
            }
        },
        {
            "type":"database",
            "data":{
                "total": 7,
                "mysqlNmb": 3,
                "mariaNum": 2,
                "postgreNum": 1,
                "auroraNum": 0,
                "cacheNum": 1
            }
        },
        {
            "type":"network",
            "data":{
                "total": 4,
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
                "total": 6,
                "objSize": "17 GiB",
                "objNum": "502 K",
                "bktPub": 1,
                "bktEncry": 5
            }
        },
        {
            "type":"st_block",
            "data":{
                "total": 20.52,
                "avaSize": "12.5 TiB",
                "useSize": "8.02 TiB"
            }
        },
        {
            "type":"st_file",
            "data":{
                "total": 3,
                "efsNum": 1,
                "efsSize": "827.7 MiB",
                "fsxNum": 2,
                "fsxSize": "3.27 GiB"
            }
        }
    ]

    resp = Result(
        detail = summaryList
        )
    return resp.make_resp()




'''数据中心资源明细(Inventory) [Mock]'''

serverList = {
    "type":"server",
    "data":[
        {
            "svrId": "i-09aa9e2c83d840ab1",
            "ebs": 8,
            "ins_type": "t4g.nano",
            "os": "Linux/UNIX",
            "pub_ip": '',
            "ram": 0.5,
            "rg_az": "us-east-1a",                
            "svr_name": "easyun-test-devbk",
            "svr_state": "stopped",
            "vcpu": 2                
        },
        {
            "svrId": "i-043e8074448089cad",
            "ebs": 20,
            "ins_type": "t4g.medium",
            "os": "Linux/UNIX",
            "pub_ip": "18.209.235.10",
            "ram": 4,
            "rg_az": "us-east-1a",            
            "svr_name": "easyun-test-notebook",
            "svr_state": "running",
            "vcpu": 2
        },
        {
            "svrId": "i-0a05f3d829d15b93a",
            "ebs": 20,
            "ins_type": "t3.nano",
            "os": "Linux/UNIX",
            "pub_ip": "3.85.106.16",
            "ram": 0.5,
            "rg_az": "us-east-1a",        
            "svr_name": "server_name124",
            "svr_state": "running",
            "vcpu": 1
        }
    ]
}

st_objectList = {
    "type":"st_object",
    "data":[
        {
        "Name": "bktexample17",
        "bucketRegion": "us-east-1",
        "bucketStatus": "Objects can be public"
        },
        {
        "Name": "easyun-api-test-13",
        "bucketRegion": "us-east-1",
        "bucketStatus": "Objects can be public"
        },
        {
        "Name": "easyun-api-test-11",
        "bucketRegion": "us-east-1",
        "bucketStatus": "Objects can be public"
        },
        {
        "Name": "easyun-api-test-12",
        "bucketRegion": "us-east-1",
        "bucketStatus": "Objects can be public"
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