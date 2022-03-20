# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Overview
  @desc:    数据中心首页(overview)相关API，包含数据中心基本信息和VPC资源分布情况
  @auth:    aleck
"""

from http import client
import re
import boto3
from datetime import datetime
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.utils import len_iter, query_dc_region, gen_dc_tag, get_subnet_type, filter_list_by_key, filter_list_by_value, set_boto3_region
from easyun.cloud.aws_region import AWS_Regions, query_country_code, query_region_name
from . import bp, logger



@bp.get('/detail')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(DCInfoOut, description='Get Datacenter Metadata')
def get_dc_detail(parm):
    '''获取指定的数据中心详细信息'''
    dcName = parm['dc']
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name=dcName).first()
        dcRegion = set_boto3_region(dcName)

        resource_ec2 = boto3.resource('ec2')
        thisVPC = resource_ec2.Vpc(thisDC.vpc_id)

        # 获取指定的数据中心基础信息
        dcBasic = {
            'dcName' : thisDC.name,
            'createDate' : thisDC.create_date.isoformat(),
            'createUser' : thisDC.create_user,
            'dcAccount' : thisDC.account_id,
            'dcRegion' : thisDC.region,
            'vpcID' : thisDC.vpc_id,
            'vpcCidr' : thisVPC.cidr_block,            
        }
 
        # 获取当前数据中心的vpc资源统计信息
        filterTag = gen_dc_tag(dcName, 'filter')
        desFilters=[
                filterTag,
                { 'Name':'vpc-id', 'Values': [ thisDC.vpc_id ] }
        ]

        natgwList = resource_ec2.meta.client.describe_nat_gateways(
            Filters = desFilters,
        ).get('NatGateways')

        subnetList = resource_ec2.meta.client.describe_subnets(
            Filters = desFilters,
        )['Subnets']

        countList = [
            { 
                'subnetTpye' : get_subnet_type(s['SubnetId']),
                'subnetAz' : s['AvailabilityZone']
            } for s in subnetList ]

        vpcSummary = {
            'pubNum': filter_list_by_value(countList,'subnetTpye','public').get('countNum'),
            'priNum': filter_list_by_value(countList,'subnetTpye','private').get('countNum'),
            'igwNum': len_iter(thisVPC.internet_gateways.all()),
            'sgNum': len_iter(thisVPC.security_groups.all()),
            'aclNum': len_iter(thisVPC.network_acls.all()),
            'rtbNum': len_iter(thisVPC.route_tables.all()),
            'eipNum': len_iter(resource_ec2.vpc_addresses.all()),
            "natNum": len(natgwList) 
        }

        # 获取当前数据中心Availability Zones分布信息
        azList = resource_ec2.meta.client.describe_availability_zones(
            Filters=[
                { 'Name': 'region-name', 'Values': [ dcRegion,] },
                { 'Name': 'state', 'Values': [ 'available',] }
            ],
        )['AvailabilityZones']
       
        azSummary = [
            {
                'azName': a['ZoneName'],
                'subnetNum' : filter_list_by_value(countList,'subnetAz', a['ZoneName']).get('countNum'),
            } for a in azList]

        resp = Result(
            detail = {
                'dcBasic': dcBasic,
                'azSummary':azSummary,
                'vpcSummary':vpcSummary
            },
            status_code=200
        )
        return resp.make_resp()
    except Exception as ex:
        response = Result(
            message= str(ex), status_code=2012, http_status_code=400
        )
        response.err_resp()
