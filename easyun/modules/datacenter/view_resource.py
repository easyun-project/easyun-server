# -*- coding: utf-8 -*-
"""
  @module:  Resource Overview
  @desc:    Resource首页(overview)相关API, 包含数据中心资源使用情况, 成本等信息
  @auth:    
"""

from calendar import firstweekday
import boto3
from datetime import datetime
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.libs.utils import len_iter
from easyun.cloud.utils import query_dc_region
from . import bp


@bp.get('/res/usage')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def get_dc_usage(parm):
    '''获取当前数据中心资源使用数据 [mock]'''
    dcName=parm.get('dc')    
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    # if (thisDC is None):
    #         response = Result(message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
    #         response.err_resp() 
  
    # client_ec2 = boto3.client('ec2', region_name= thisDC.region)
    resource_ec2 = boto3.resource('ec2', region_name= thisDC.region)
    # dcVPC = resource_ec2.Vpc(thisDC.vpc_id)

    VPCUsedNum = len_iter(resource_ec2.vpcs.all())
    SecurityGroupUsedNum = len_iter(resource_ec2.security_groups.all())
    SubnetsUsedNum = len_iter(resource_ec2.subnets.all())
    EipUsedNum = len_iter(resource_ec2.vpc_addresses.all())
    IgwUsedNum = len_iter(resource_ec2.internet_gateways.all())
    NetworkInterfaceUsedNum = len_iter(resource_ec2.network_interfaces.all())

    usageList = []
    dcUsage = {
            'vpcNum' : VPCUsedNum,
            'subnetNum': SubnetsUsedNum,
            'igwNum': IgwUsedNum,
            'natNum' : 5,
            'eipNum' : EipUsedNum,            
            'eniNum': NetworkInterfaceUsedNum,
            'secgroupNum' : SecurityGroupUsedNum,
            }
    usageList.append(dcUsage)

    svrUsage = {
            'instanceNum' : 12,

            }
    usageList.append(svrUsage)

    strUsage = {
            'blockNum' : 14,
            'fileNum' : 3,            
            }
    usageList.append(strUsage)

    resp = Result(
        detail = usageList,
        status_code=200
    )

    return resp.make_resp()

    # dcUsageList = [
    #     {
    #         "vpcname": "vip1",
    #         'vpcId': 'vpc-0a818f9a74c0657ad',
    #         'EIP usage': '3/5 is being used',
    #         'Subnet usage': '3/5 is being used'
    #     },
    #     {
    #         "vpcname": "vip2",
    #         'vpcId': 'vpc-0a818f9a74c0657ad',
    #         'EIP usage': '3/5 is being used',
    #         'Subnet usage': '3/5 is being used'
    #     }
    # ]

    # resp = Result(
    #     detail = dcUsageList,
    #     status_code=200
    # )
    # return resp.make_resp()


@bp.get('/res/cost')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SecgroupsOut, description='List DataCenter SecurityGroups Resources')
def get_res_cost(parm):
    '''获取当前数据中心资源月度成本 [mock]'''
    dcName=parm.get('dc')

    today = datetime.date.today()
    firstDay = get_month_range(today).get('firstDay')
    lastDay = get_month_range(today).get('lastDay')
    # start_month_date = (today - dateutil.relativedelta.relativedelta(months=12))

    start_date = "{}-{:02d}-{:02d}".format(today.year, today.month, 1)
    end_date = "{}-{:02d}-{:02d}".format(today.year, today.month, today.day)
    last_day = "{}-{:02d}-{:02d}".format(lastDay.year, lastDay.month, lastDay.day)

    client_ce = boto3.client('ce', region_name = 'us-east-1')
    result = client_ce.get_cost_and_usage(
        TimePeriod = {
            'Start': start_date,
            'End': end_date
        },
        Granularity = 'MONTHLY',
        Filter = {
            "Tags": {
                        "Key": "Flag",
                        "Values": [dcName]
                    }
        },
        Metrics = ["BlendedCost"],
        GroupBy = [
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            },
            {
                'Type': 'DIMENSION',
                'Key': 'USAGE_TYPE'
            }
        ]
    )
    return result["ResultsByTime"]

# Compute dates
def get_month_range(any_day):
    # this will never fail
    # get close to the end of the month for any day, and add 4 days 'over'
    # next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
    return {
        'firstDay':'2022-1-1',
        'lastDay':'2022-1-31',
    }