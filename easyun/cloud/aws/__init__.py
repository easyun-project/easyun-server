# -*- coding: utf-8 -*-
"""
  @module:  Easyun Cloud SDK Module
  @desc:    Easyun Cloud Account and Resource Wrapper.
  @auth:    aleck
"""

from botocore.exceptions import ClientError
from easyun.common.models import Datacenter
from ..aws_region import query_country_code, query_region_name
from ..utils import get_easyun_session
from .sdk_datacenter import DataCenter, Subnet, InternetGateway, NatGateway, SecurityGroup, StaticIP


_DATACENTER = None
_SUBNET = None
_SECURITY_GROUP = None
_INT_GATEWAY = None
_NAT_GATEWAY = None
_STATIC_IP = None


def get_datacenter(dc_name):
    global _DATACENTER
    if _DATACENTER is not None and _DATACENTER.dcName == dc_name:
        return _DATACENTER
    else:
        return DataCenter(dc_name)


def get_subnet(subnet_id, dc_name):
    global _SUBNET
    if _SUBNET is not None and _SUBNET.dcName == dc_name:
        return _SUBNET
    else:
        return Subnet(subnet_id, dc_name)


def get_secgroup(sg_id, dc_name):
    global _SECURITY_GROUP
    if _SECURITY_GROUP is not None and _SECURITY_GROUP.sgId == sg_id:
        return _SECURITY_GROUP
    else:
        return SecurityGroup(sg_id, dc_name)


def get_int_gateway(igw_id, dc_name):
    global _INT_GATEWAY
    if _INT_GATEWAY is not None and _INT_GATEWAY.igwId == dc_name:
        return _INT_GATEWAY
    else:
        return InternetGateway(igw_id, dc_name)


def get_nat_gateway(natgw_id, dc_name):
    global _NAT_GATEWAY
    if _NAT_GATEWAY is not None and _NAT_GATEWAY.natgwId == natgw_id:
        return _NAT_GATEWAY
    else:
        return NatGateway(natgw_id, dc_name)


def get_staticip(eip_id, dc_name):
    global _STATIC_IP
    if _STATIC_IP is not None and _STATIC_IP.allocId == eip_id:
        return _STATIC_IP
    else:
        return StaticIP(eip_id, dc_name)


class AWSCloud(object):
    def __init__(self, account_id, region_type='Global'):
        self.accountId = account_id
        self.regionType = region_type
        self.session = get_easyun_session()
        self.dcs = Datacenter.query.filter_by(account_id=self.accountId)

    def list_all_datacenter(self):
        '''list all datacenter in the account'''
        try:
            datacenterList = []
            for dc in self.dcs:
                resource_ec2 = self.session.resource('ec2', region_name=dc.region)
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
            for dc in self.dcs:
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
        '''get a datacenter brief list in the account'''
        try:
            if self.regionType == 'GCR':
                regionList = self.session.get_available_regions(service_name, 'aws-cn')
            else:
                # aws_type == Global
                regionList = self.session.get_available_regions(service_name)
            return [
                {
                    'regionCode': r,
                    'regionName': query_region_name(r),
                    'countryCode': query_country_code(r),
                } for r in regionList
            ]
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
