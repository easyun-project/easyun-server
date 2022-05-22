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


class AWSCloud(object):
    def __init__(self, account_id, account_type='Global'):
        self.accountId = account_id
        self.account_type = account_type
        self.session = get_easyun_session()
        self.all_dc = Datacenter.query.filter_by(account_id=self.accountId)

    def list_all_datacenter(self):
        '''list all datacenter in the account'''
        try:
            datacenterList = []
            for dc in self.all_dc:
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
            for dc in self.all_dc:
                dcItem = {'dcName': dc.name, 'regionCode': dc.region, 'vpcID': dc.vpc_id}
                datacenterList.append(dcItem)
            return datacenterList
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_region_list(self, service_name):
        '''get a datacenter brief list in the account'''
        try:
            if self.account_type == 'GCR':
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

