# -*- coding: utf-8 -*-
"""
  @module:  Dashboard Inventory
  @desc:    DataCenter resource inventory, including: server,storage,rds,networking,etc.
  @auth:    
"""

import boto3
from apiflask import auth_required, Schema
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import len_iter, filter_list_by_key
from easyun.cloud.aws_basic import get_deploy_env
from easyun.cloud.aws_region import AWS_Regions, query_country_code, query_region_name
from .api_inventory import query_inventory
from .models import Boto3_Cloudwatch
from . import bp, DeployRegion



@bp.get("/summary/datacenter")
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def summary_dc(parm):
    '''获取数据中心 Summary信息'''
    thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
    dcRegion = thisDC.get_region()
    # dcVPC = thisDC.get_vpc()

    # 从AWS Region列表中匹配 当前 region 信息
    regionDict = [region for region in AWS_Regions if region['regionCode']==dcRegion][0]
    regionInfo = {
        "icon" : regionDict.get('countryCode'),
        "name" : regionDict.get('regionName')['eng']
    }

    client_ec2 = boto3.client('ec2', region_name= dcRegion)
    azs = client_ec2.describe_availability_zones()

    summaryList = []
    for az in azs['AvailabilityZones']:
        azName = az.get('ZoneName')
    
        subnetResp = client_ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Flag',
                    'Values': [
                        parm['dc'],
                    ]
                },
                {
                    'Name':'availability-zone',
                    'Values': [
                        azName
                    ]
                }
            ],
        )
        subnetNum = len(subnetResp.get('Subnets'))
        azStatus = 'running' if subnetNum else 'empty'
        
        azItem = {
            "azName": azName,
            "azStatus": azStatus,
            "subnetNum": subnetNum,
            "dcRegion": regionInfo
        }
        summaryList.append(azItem) 

    resp = Result(
        detail = summaryList
        )
    return resp.make_resp()



@bp.get("/summary/health")
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def summary_health(parm):
    '''获取健康状态 Summary信息'''
    thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
    dcRegion = thisDC.get_region() 
    try:
        # 设置 boto3 接口默认 region_name
        # boto3.setup_default_session(region_name=dcRegion)

        cwSdk = Boto3_Cloudwatch(dcRegion)        
        alarms = cwSdk.get_alarms()
        dashboards = cwSdk.get_dashboards()
        summary_list = {
            "alarms": alarms,
            "dashboards": dashboards
        }
        resp = Result(
            detail=summary_list
        )
        return resp.make_resp()

    except Exception as e:
        resp = Result(
            detail=str(e),
            status_code=7010
        )
        return resp.err_resp()


@bp.get("/summary/resource")
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def summary_resource(parm):
    '''获取所有IaaS资源 Summary信息'''
    dcName = parm['dc']
    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = DeployRegion)

    # Summary server
    serverList = query_inventory('server', dcName).get('data')
    stateList = filter_list_by_key(serverList,'svrState')
    vcpuList = filter_list_by_key(serverList,'vpuNum')
    ramList = filter_list_by_key(serverList,'ramSize')
    serverSum = {
        "type":"server",
        'data':{
            "sumNum": len(serverList),
            "runNum": stateList.count('running'),
            "stopNum": stateList.count('running'),
            "vcpuNum": sum([int(i) for i in vcpuList]),
            "ramSize": {
                'value':sum([float(i) for i in ramList]),
                'unit':'GiB'
            }
        }
    }

    # Summary database
    databaseList = query_inventory('database', dcName).get('data')
    engineList = filter_list_by_key(databaseList,'dbiEngine')
    
    databaseSum = {
        "type":"database",
        "data":{
            "sumNum": len(databaseList),
            # ['aurora','aurora-mysql','aurora-postgresql']
            "auroraNum": engineList.count('aurora-mysql'),
            "mysqlNum": engineList.count('mysql'),
            "mariaNum": engineList.count('mariadb'),
            "postgreNum": engineList.count('postgres'),
            'cacheNum': 0,
            # ['oracle-ee','oracle-ee-cdb','oracle-se2','oracle-se2-cdb']
            "oracleNum": engineList.count('sqlserver'),            
            # ['sqlserver-ee','sqlserver-se','sqlserver-ex','sqlserver-web']
            "sqlserverNum": engineList.count('sqlserver'),
        }
    }

    # Summary network
    subnetList = query_inventory('nw_subnet', dcName).get('data')
    typeList = filter_list_by_key(subnetList,'subnetType')
    secgroupList = query_inventory('nw_secgroup', dcName).get('data')
    # gatewayList = query_inventory('nw_gateway', dcName).get('data')
    networkSum = {
            "type":"network",
            "data":{
                "sumNum": len(subnetList),
                "pubNum": typeList.count('public'),
                "priNum": typeList.count('private'),
                "igwNum": 1,
                "natNum": 1,
                "sgNum": len(secgroupList),
            }
    }

    # Summary st_object
    objectList = query_inventory('st_object', dcName).get('data')
    accessList = filter_list_by_key(objectList,'bktAccess')
    sizeList = filter_list_by_key(objectList,'bktSize')
    encList = filter_list_by_key(objectList,'isEncrypted')    
    stobjectSum = {
            "type":"st_object",
            "data":{
                "sumNum": len(objectList),
                "objSize": {
                    'value':sum([int(i['value']) for i in sizeList])/1024/1024,
                    'unit':'MiB'
                },
                "objNum": 32013,
                "pubNum": accessList.count('public'),
                "encNum": encList.count(True)
            }
    }

    # Summary st_block
    blockList = query_inventory('st_block', dcName).get('data')
    stateList = filter_list_by_key(blockList,'volumeState')
    sizeList = filter_list_by_key(blockList,'volumeSize')
    encList = filter_list_by_key(blockList,'isEncrypted')
    stblockSum = {
            "type":"st_block",
            "data":{
                "sumNum": len(blockList),
                "blcSize": {
                    'value': sum([int(i) for i in sizeList]),
                    'unit':'GiB'
                },
                "useNum": stateList.count('in-use'),
                "avlNum": stateList.count('available'),
                "encNum": encList.count(True),
            }
    }

    # Summary st_files
    filesList = query_inventory('st_files', dcName).get('data')
    '''Mock data'''
    stfileSum = {
        "type":"st_files",
        "data":{
            "sumNum": 3,
            "efsNum": len(filesList),
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

    resp = Result(
        detail = [
            serverSum, databaseSum,networkSum,stobjectSum,stblockSum,stfileSum
        ]
        )
    return resp.make_resp()
