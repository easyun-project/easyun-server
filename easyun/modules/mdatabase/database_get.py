# -*- coding: utf-8 -*-
"""
  @module:  Database Get Module
  @desc:    数据库相关信息GET API
  @auth:    aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.utils import len_iter, query_dc_region
from datetime import date, datetime
from . import bp


@bp.get('')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_database_detail(parm):
    '''获取数据中心全部数据库(RDS)信息【未完成】'''

    dcName = parm['dc']
    try:
        thisDC = Datacenter.query.filter_by(name = dcName).first()
        dcRegion = thisDC.get_region()

        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_rds = boto3.client('rds')
        dbis = client_rds.describe_db_instances(
            # Filters=[
            #     { 'Name': 'tag:Flag', 'Values': [dcName,]},
            # ],
            # DBInstanceIdentifier='string',            
        )
        dbiList = []
        for db in dbis['DBInstances']:
            dbiItem = {
                'dbiId': db['DBInstanceIdentifier'],
                'dbiEngine': db['Engine'],
                'engineVer': db['EngineVersion'],
                'dbiStatus': 'available',
                'dbiSize': db['DBInstanceClass'],
                'vcpuNum': 1,
                'ramSize': 2,
                'volumeSize': 20,
                'dbiAz': db['AvailabilityZone'],
                'multiAz': db['MultiAZ'],
                'dbiEndpoint': db['Endpoint'].get('Address'),
                # 'createTime': db['InstanceCreateTime'].isoformat()
            }
            
            # filter不支持tag过滤条件，手动判断Flag标记
            flagTag = next((tag['Value'] for tag in db['TagList'] if tag["Key"] == 'Flag'), None)
            if flagTag == dcName:
                    dbiList.append(dbiItem)

        resp = Result(
            detail = dbiList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message = ex, 
            status_code=5000,
            http_status_code=400
        )
        return resp.err_resp()

@bp.get('/<rds_id>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def get_database_detail(rds_id, parm):
    '''获取指定数据库(RDS)详细信息'''
    pass


@bp.get('/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SvrListOut, description='Get Servers list')
def list_database_brief(parm):
    '''获取数据中心全部数据库(RDS)列表[仅基础字段]'''

    dcName = parm['dc']
    try:
        thisDC = Datacenter.query.filter_by(name = dcName).first()
        dcRegion = thisDC.get_region()

        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )

        client_rds = boto3.client('rds')
        dbis = client_rds.describe_db_instances()
        dbiList = []
        for db in dbis['DBInstances']:
            dbiItem = {
                'dbiId': db['DBInstanceIdentifier'],
                'dbiEngine': db['Engine'],
                'dbiStatus': 'available',
                'dbiSize': db['DBInstanceClass'],
                'dbiAz': db['AvailabilityZone'],
            }
            
            # filter不支持tag过滤条件，手动判断Flag标记
            flagTag = next((tag['Value'] for tag in db['TagList'] if tag["Key"] == 'Flag'), None)
            if flagTag == dcName:
                    dbiList.append(dbiItem)

        resp = Result(
            detail = dbiList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message = ex, 
            status_code=5000,
            http_status_code=400
        )
        return resp.err_resp()
