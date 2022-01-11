# -*- coding: utf-8 -*-
"""dashboard model views."""

from apiflask import Schema, input, output, auth_required
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account


@bp.get("/dc_summary")
@auth_required(auth_token)
# @output(SummaryOut)
def dc_summary():
    '''获取 数据中心 Summary信息'''
    dcSummary = [
      {
        "az": "us-east-1a",
        "azName": "US East (N. Virginia)",
        "icon": "us",
        "empty": 0,
        "subnet": 2
      },
      {
        "az": "us-east-1b",
        "azName": "US East (N. Virginia)",
        "icon": "us",
        "empty": 0,
        "subnet": 2
      },
      {
        "az": "us-east-1c",
        "azName": "US East (N. Virginia)",
        "icon": "us",
        "empty": 1,
        "subnet": 0
      },
      {
        "az": "us-east-1d",
        "azName": "US East (N. Virginia)",
        "icon": "us",
        "empty": 1,
        "subnet": 0
      },
      {
        "az": "us-east-1e",
        "azName": "US East (N. Virginia)",
        "icon": "us",
        "empty": 1,
        "subnet": 0
      }
    ]

    resp = Result(
        detail = dcSummary
        )
    return resp.make_resp()   



@bp.get("/health")
@auth_required(auth_token)
# @output(SummaryOut)
def health_summary():
    '''获取 健康状态 Summary信息'''    
    healthSumary = {
        "alarms": {
            "ia": "1",
            "id": "3",
            "ok": "2"
        },
        "favorite": {
            "Easyun Overview": "http://www.aws-cloudwatch.com/xxxx",
            "EC2 Dashboard": "http://www.aws-cloudwatch.com/xxxx",
            "RDS Dashobard": "http://www.aws-cloudwatch.com/xxxx",
            "Storage": "http://www.aws-cloudwatch.com/xxxx"
        }
    }

    resp = Result(
        detail = healthSumary
        )
    return resp.make_resp()



@bp.get("/graph")
@auth_required(auth_token)
# @output(SummaryOut)
def graph_summary():
    '''获取 IaaS资源 Summary信息''' 
    graphSummary = {
        "server":{
            "sum": 19,
            "run": 15,
            "stop": 4,
            "vcpu": 76,
            "ram": 119
        },
        "database":{
            "sum": 7,
            "mysql": 3,
            "mariadb": 2,
            "postgre": 1,
            "aurora": 0,
            "elasticach": 1
        },
        "network":{
            "sum": 4,
            "pub": 2,
            "pri": 2,
            "igw": 1,
            "nat": 1,
            "sg": 3
        },
        "storage_obj":{
            "sum": 6,
            "size": "17 GiB",
            "count": "502 K",
            "pub": 1,
            "encry": 5
        },
            "storage_block":{
            "sum": 12.5,
            "total": "20.52 TiB",
            "used": "8.02 TiB"
        },
        "storage_file":{
            "num": 3,
            "efs": 1,
            "efs_size": "827.7 MiB",
            "fsx": 2,
            "fsx_size": "3.27 GiB"
        }
    }

    resp = Result(
        detail = graphSummary
        )
    return resp.make_resp()


@bp.get("/list")
@auth_required(auth_token)
# @output(SummaryOut)
def view_list():
    '''获取 IaaS资源 list明细清单'''
    serverList = [
        {
        "ebs": 8,
        "ins_type": "t4g.nano",
        "os": "Linux/UNIX",
        "pub_ip": '',
        "ram": 0.5,
        "rg_az": "us-east-1a",
        "svr_id": "i-09aa9e2c83d840ab1",
        "svr_name": "easyun-test-devbk",
        "svr_state": "stopped",
        "vcpu": 2
        },
        {
        "ebs": 20,
        "ins_type": "t4g.medium",
        "os": "Linux/UNIX",
        "pub_ip": "18.209.235.10",
        "ram": 4,
        "rg_az": "us-east-1a",
        "svr_id": "i-043e8074448089cad",
        "svr_name": "easyun-test-notebook",
        "svr_state": "running",
        "vcpu": 2
        },
        {
        "ebs": 20,
        "ins_type": "t3.nano",
        "os": "Linux/UNIX",
        "pub_ip": "3.85.106.16",
        "ram": 0.5,
        "rg_az": "us-east-1a",
        "svr_id": "i-0a05f3d829d15b93a",
        "svr_name": "server_name124",
        "svr_state": "running",
        "vcpu": 1
        }
    ]

    storageList = [
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

    resp = Result(
        detail={
            'serverList' : serverList,
            'storageList' : storageList
        }
    )
    return resp.make_resp()