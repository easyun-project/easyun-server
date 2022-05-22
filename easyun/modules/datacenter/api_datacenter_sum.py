# -*- coding: utf-8 -*-
"""
  @module:  DataCenter & Resource Overview
  @desc:    首页(overview)相关API, 数据中心VPC基本信息和各项服务/资源使用情况, 成本等信息
  @auth:    aleck
"""

import boto3
from datetime import datetime, date, timedelta
from apiflask import input, output, auth_required
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.libs.utils import len_iter, filter_list_by_key, filter_list_by_value
from easyun.cloud.utils import gen_dc_tag, get_subnet_type, set_boto3_region
from easyun.cloud.sdk_tagging import ResGroupTagging
from easyun.cloud.sdk_cost import CostExplorer, get_ce_region
from . import bp, logger


@bp.get('/summary/basic')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(DCInfoOut, description='Get Datacenter Metadata')
def get_vpc_summary(parm):
    '''获取指定的数据中心VPC基础服务统计信息'''
    dcName = parm['dc']
    try:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dcName).first()
        dcRegion = set_boto3_region(dcName)

        resource_ec2 = boto3.resource('ec2')
        thisVPC = resource_ec2.Vpc(thisDC.vpc_id)

        filterTag = gen_dc_tag(dcName, 'filter')
        desFilters = [filterTag, {'Name': 'vpc-id', 'Values': [thisDC.vpc_id]}]

        natgwList = resource_ec2.meta.client.describe_nat_gateways(
            Filters=desFilters,
        ).get('NatGateways')

        subnetList = resource_ec2.meta.client.describe_subnets(
            Filters=desFilters,
        )['Subnets']

        countList = [
            {
                'subnetType': get_subnet_type(s['SubnetId']),
                'subnetAz': s['AvailabilityZone'],
            }
            for s in subnetList
        ]

        vpcSummary = {
            'pubNum': filter_list_by_value(countList, 'subnetType', 'public').get(
                'countNum'
            ),
            'priNum': filter_list_by_value(countList, 'subnetType', 'private').get(
                'countNum'
            ),
            'igwNum': len_iter(thisVPC.internet_gateways.all()),
            'sgNum': len_iter(thisVPC.security_groups.all()),
            'aclNum': len_iter(thisVPC.network_acls.all()),
            'rtbNum': len_iter(thisVPC.route_tables.all()),
            'eipNum': len_iter(resource_ec2.vpc_addresses.all()),
            "natNum": len(natgwList),
        }

        # 获取当前数据中心Availability Zones分布信息
        azList = resource_ec2.meta.client.describe_availability_zones(
            Filters=[
                {
                    'Name': 'region-name',
                    'Values': [
                        dcRegion,
                    ],
                },
                {
                    'Name': 'state',
                    'Values': [
                        'available',
                    ],
                },
            ],
        )['AvailabilityZones']

        azSummary = [
            {
                'azName': a['ZoneName'],
                'subnetNum': filter_list_by_value(
                    countList, 'subnetAz', a['ZoneName']
                ).get('countNum'),
            }
            for a in azList
        ]

        resp = Result(
            detail={'azSummary': azSummary, 'vpcSummary': vpcSummary}, status_code=200
        )
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2012, http_status_code=400)
        response.err_resp()


@bp.get('/summary/resource')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(DCInfoOut, description='Get Datacenter Metadata')
def get_res_summary(parm):
    '''获取指定的数据中心Resource统计信息'''
    dcName = parm['dc']
    dcRegion = set_boto3_region(dcName)
    try:
        rgt = ResGroupTagging(dcName)
        resSummary = {
            'serverNum': rgt.sum_resources('ec2:instance'),
            'volumeNum': rgt.sum_resources('ec2:volume'),
            'bucketNum': rgt.sum_resources('s3:bucket'),
            'efsNum': rgt.sum_resources('elasticfilesystem:file-system'),
            'rdsNum': rgt.sum_resources('rds:db'),
            'elbNum': rgt.sum_resources('elasticloadbalancing:loadbalancer'),
            'elbtgNum': rgt.sum_resources('elasticloadbalancing:targetgroup'),
            'volbackupNum': rgt.sum_resources('ec2:snapshot'),
            'rdsbackupNum': rgt.sum_resources('rds:snapshot'),
            'efsbackupNum': rgt.sum_resources('backup:recovery-point'),
        }
        resp = Result(detail=resSummary, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2012, http_status_code=400)
        response.err_resp()


@bp.get('/summary/cost')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def get_cost_summary(parm):
    '''获取指定的数据中心成本及用量统计信息'''
    dcName = parm['dc']
    thisAccount: Account = Account.query.first()
    try:
        # 根据账号类型选择对应 api endpoint
        ceRegion = get_ce_region(thisAccount.aws_type)
        ce = CostExplorer(dcName, region=ceRegion)

        # get last month
        todayDate = date.today()
        lastMonthDate = todayDate.replace(day=1) - timedelta(days=1)
        lastMonth = lastMonthDate.strftime('%Y-%m')

        costSummary = {
            'currMonthTotal': ce.get_monthly_total_cost(),
            'forecastTotal': ce.get_forecast_total_cost(),
            'lastMonthTotal': ce.get_monthly_total_cost(lastMonth),
            'currMonthCost': ce.get_a_month_cost_list(),
            'latestWeekCost': ce.get_latest_week_daily_cost(),
        }
        resp = Result(detail=costSummary, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2012, http_status_code=400)
        response.err_resp()
