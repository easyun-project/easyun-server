# -*- coding: utf-8 -*-
"""
  @module:  Database Get Module
  @desc:    数据库相关信息GET API
  @auth:    aleck
"""

import boto3
from apiflask import auth_required, Schema
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.common.utils import gen_dc_tag, len_iter, set_boto3_region, query_dc_region
from datetime import date, datetime
from . import bp


@bp.get('')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def list_database_detail(parm):
    '''获取数据中心全部数据库(RDS)信息'''
    dcName = parm['dc']
    try:
        thisDC = Datacenter.query.filter_by(name = dcName).first()
        dcRegion = set_boto3_region(dcName)

        client_rds = boto3.client('rds')
        # filterTag = gen_dc_tag(dcName, type='filter')        
        dbis = client_rds.describe_db_instances(
            # Filters=[ filterTag ],       
        )
        dbiList = []
        for dbi in dbis['DBInstances']:
            # filter不支持tag过滤条件，手动判断Flag标记
            flagTag = next((tag['Value'] for tag in dbi['TagList'] if tag["Key"] == 'Flag'), None)
            if flagTag == dcName:
                dbiItem = {
                    'dbiId': dbi['DBInstanceIdentifier'],
                    'dbiEngine': dbi['Engine'],
                    'engineVer': dbi['EngineVersion'],
                    'dbiStatus': 'available',
                    'dbiSize': dbi['DBInstanceClass'],
                    'vcpuNum': 1,
                    'ramSize': 2,
                    'volumeSize': 20,
                    'dbiAz': dbi['AvailabilityZone'],
                    'multiAz': dbi['MultiAZ'],
                    'dbiEndpoint': dbi['Endpoint'].get('Address'),
                    # 'createTime': dbi['InstanceCreateTime'].isoformat()
                }
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
@bp.input(DcNameQuery, location='query')
def get_database_detail(rds_id, parm):
    '''获取指定数据库(RDS)详细信息'''
    dcName = parm['dc']
    try:
        dcRegion = set_boto3_region(dcName)
        client_rds = boto3.client('rds')
        dbis = client_rds.describe_db_instances(
            DBInstanceIdentifier= rds_id,            
        )
        dbiList = []
        for dbi in dbis['DBInstances']:
            dbiTags = [tag for tag in dbi['TagList'] if tag["Key"] != 'Flag']
            dbiItem = {
                'dbiId': dbi['DBInstanceIdentifier'],
                'dbiEngine': dbi['Engine'],
                'engineVer': dbi['EngineVersion'],
                'dbiStatus': 'available',
                'dbiSize': dbi['DBInstanceClass'],
                'vcpuNum': 1,
                'ramSize': 2,
                'volumeSize': 20,
                'dbiAz': dbi['AvailabilityZone'],
                'multiAz': dbi['MultiAZ'],
                'dbiEndpoint': dbi['Endpoint'].get('Address'),
                'createTime': dbi['InstanceCreateTime'].isoformat(),
                'dbiTags': dbiTags
            }
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


@bp.get('/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @bp.output(SvrListOut, description='Get Servers list')
def list_database_brief(parm):
    '''获取数据中心全部数据库(RDS)列表[仅基础字段]'''

    dcName = parm['dc']
    try:
        dcRegion = set_boto3_region(dcName)
        client_rds = boto3.client('rds')
        dbis = client_rds.describe_db_instances()

        dbiList = []
        for dbi in dbis['DBInstances']:
            # filter不支持tag过滤条件，手动判断Flag标记
            flagTag = next((tag['Value'] for tag in dbi['TagList'] if tag["Key"] == 'Flag'), None)
            if flagTag == dcName:
                dbiItem = {
                    'dbiId': dbi['DBInstanceIdentifier'],
                    'dbiEngine': dbi['Engine'],
                    'dbiStatus': 'available',
                    'dbiSize': dbi['DBInstanceClass'],
                    'dbiAz': dbi['AvailabilityZone'],
                }
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
