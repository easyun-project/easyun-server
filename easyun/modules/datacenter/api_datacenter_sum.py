# -*- coding: utf-8 -*-
"""
  @module:  DataCenter & Resource Overview
  @desc:    首页(overview)相关API, 数据中心VPC基本信息和各项服务/资源使用情况, 成本等信息
  @auth:    aleck
"""

from datetime import date, timedelta
from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.libs.utils import filter_list_by_value
from easyun.cloud.utils import get_subnet_type
from easyun.cloud.aws.sdk_cost import CostExplorer, get_ce_region
from easyun.cloud.aws import get_datacenter
from easyun.cloud.utils import set_boto3_region
from . import bp, logger


@bp.get('/summary/basic')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @output(DCInfoOut, description='Get Datacenter Metadata')
def get_vpc_summary(parm):
    '''获取指定的数据中心VPC基础服务统计信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        subnetList = dc._client.describe_subnets(
            Filters=[dc.tagFilter, {'Name': 'vpc-id', 'Values': [dc.vpcId]}],
        )['Subnets']
        countList = [
            {
                'subnetType': get_subnet_type(subnet['SubnetId']),
                'azName': subnet['AvailabilityZone'],
            }
            for subnet in subnetList
        ]

        vpcSummary = {
            'pubNum': filter_list_by_value(countList, 'subnetType', 'public').get(
                'countNum'
            ),
            'priNum': filter_list_by_value(countList, 'subnetType', 'private').get(
                'countNum'
            ),
            'igwNum': dc.count_resource('igw'),
            'sgNum': dc.count_resource('secgroup'),
            'aclNum': dc.count_resource('nacl'),
            'rtbNum': dc.count_resource('rtb'),
            # 'eipNum': len_iter(resource_ec2.vpc_addresses.all()),
            'eipNum': dc.count_resource('staticip'),
            "natNum": dc.count_resource('natgw'),
        }

        # 获取当前数据中心Availability Zones分布信息
        azList = dc.get_azone_list()

        azSummary = [
            {
                'azName': az,
                'subnetNum': filter_list_by_value(countList, 'azName', az).get('countNum'),
            }
            for az in azList
        ]

        resp = Result(
            detail={
                'azSummary': azSummary,
                'vpcSummary': vpcSummary
            }
        )
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2012, http_status_code=400)
        response.err_resp()


@bp.get('/summary/resource')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @output(DCInfoOut, description='Get Datacenter Metadata')
def get_res_summary(parm):
    '''获取指定的数据中心Resource统计信息'''
    dcName = parm['dc']
    try:
        # 设置默认region兼容旧api写法
        set_boto3_region(dcName)

        dc = get_datacenter(dcName)
        rgt = dc.tagging
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
@bp.input(DcNameQuery, location='query')
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
