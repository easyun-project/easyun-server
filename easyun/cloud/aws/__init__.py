# -*- coding: utf-8 -*-
"""
  @module:  Easyun Cloud SDK Module
  @desc:    Easyun Cloud Account and Resource Wrapper.
  @auth:    aleck
"""

from botocore.exceptions import ClientError
from easyun.common.models import Datacenter
from .session import get_easyun_session
from .region import query_country_code, query_region_name
from .datacenter import DataCenter, Subnet, RouteTable, InternetGateway, NatGateway, SecurityGroup, StaticIP


def get_datacenter(dc_name):
    return DataCenter(dc_name)


def get_subnet(subnet_id, dc_name):
    return Subnet(subnet_id, dc_name)


def get_routetable(rtb_id, dc_name):
    return RouteTable(rtb_id, dc_name)


def get_secgroup(sg_id, dc_name):
    return SecurityGroup(sg_id, dc_name)


def get_int_gateway(igw_id, dc_name):
    return InternetGateway(igw_id, dc_name)


def get_nat_gateway(natgw_id, dc_name):
    return NatGateway(natgw_id, dc_name)


def get_staticip(eip_id, dc_name):
    return StaticIP(eip_id, dc_name)


class AWSCloud(object):
    def __init__(self, account_id, region_type='Global'):
        self._session = get_easyun_session()
        self.accountId = account_id
        self.regionType = region_type
        self.datacenters = Datacenter.query.filter_by(account_id=self.accountId)

    def list_all_datacenter(self):
        '''list all datacenter in the account'''
        try:
            datacenterList = []
            for dc in self.datacenters:
                resource_ec2 = self._session.resource('ec2', region_name=dc.region)
                # error handing for InvalidVpcID.NotFound
                try:
                    vpc = resource_ec2.Vpc(dc.vpc_id)
                    dcItem = {
                        'dcName': dc.name,
                        'regionCode': dc.region,
                        'vpcID': dc.vpc_id,
                        'cidrBlock': vpc.cidr_block,
                        'createDate': dc.create_date,
                        'createUser': dc.create_user,
                        'accountId': dc.account_id,
                    }
                    datacenterList.append(dcItem)
                except ClientError:
                    continue
            return datacenterList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_datacenter_list(self):
        '''get a datacenter brief list in the account'''
        try:
            datacenterList = []
            for dc in self.datacenters:
                dcItem = {
                    'dcName': dc.name,
                    'regionCode': dc.region,
                    'vpcID': dc.vpc_id
                }
                datacenterList.append(dcItem)
            return datacenterList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_region_list(self, service_name):
        '''get region list in AWS Cloud'''
        try:
            if self.regionType == 'GCR':
                regionList = self._session.get_available_regions(service_name, 'aws-cn')
            else:
                # aws_type == Global
                regionList = self._session.get_available_regions(service_name)
            return [
                {
                    'regionCode': r,
                    'regionName': query_region_name(r),
                    'countryCode': query_country_code(r),
                } for r in regionList
            ]
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def create_datacenter(self, dc_parms, user):
        try:
            pass
            return DataCenter(self.dcName)
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
