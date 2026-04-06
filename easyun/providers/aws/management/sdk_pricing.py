# -*- coding: utf-8 -*-
"""
  @module:  AWS Pricing SDK
  @desc:    AWS Price List API wrapper.
"""

import ast
import boto3


INSTANCE_TYPE_URL = 'https://aws.amazon.com/cn/ec2/instance-types/'
VOLUME_TYPE_URL = 'https://aws.amazon.com/cn/ebs/volume-types/'

# AWS Price API only support us-east-1, ap-south-1
PRICE_REGION_LIST = ['us-east-1', 'ap-south-1']

# Platform to Usage Operation mapping
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/billing-info-fields.html
Platform_to_Operation = [
    {'platformDetails': 'Linux/UNIX', 'usageOperation': 'RunInstances'},
    {'platformDetails': 'Red Hat BYOL Linux', 'usageOperation': 'RunInstances:00g0'},
    {'platformDetails': 'Red Hat Enterprise Linux', 'usageOperation': 'RunInstances:0010'},
    {'platformDetails': 'Red Hat Enterprise Linux with HA', 'usageOperation': 'RunInstances:1010'},
    {'platformDetails': 'Red Hat Enterprise Linux with SQL Server Standard and HA', 'usageOperation': 'RunInstances:1014'},
    {'platformDetails': 'Red Hat Enterprise Linux with SQL Server Enterprise and HA', 'usageOperation': 'RunInstances:1110'},
    {'platformDetails': 'Red Hat Enterprise Linux with SQL Server Standard', 'usageOperation': 'RunInstances:0014'},
    {'platformDetails': 'Red Hat Enterprise Linux with SQL Server Web', 'usageOperation': 'RunInstances:0210'},
    {'platformDetails': 'Red Hat Enterprise Linux with SQL Server Enterprise', 'usageOperation': 'RunInstances:0110'},
    {'platformDetails': 'SQL Server Enterprise', 'usageOperation': 'RunInstances:0100'},
    {'platformDetails': 'SQL Server Standard', 'usageOperation': 'RunInstances:0004'},
    {'platformDetails': 'SQL Server Web', 'usageOperation': 'RunInstances:0200'},
    {'platformDetails': 'SUSE Linux', 'usageOperation': 'RunInstances:000g'},
    {'platformDetails': 'Windows', 'usageOperation': 'RunInstances:0002'},
    {'platformDetails': 'Windows BYOL', 'usageOperation': 'RunInstances:0800'},
    {'platformDetails': 'Windows with SQL Server Enterprise *', 'usageOperation': 'RunInstances:0102'},
    {'platformDetails': 'Windows with SQL Server Standard', 'usageOperation': 'RunInstances:0006'},
    {'platformDetails': 'Windows with SQL Server Web', 'usageOperation': 'RunInstances:0202'},
]

OS_Code_List = ['amzn2', 'ubuntu', 'debian', 'linux', 'rhel', 'sles', 'windows']

OS_MAP = {
    'amzn2': 'Linux', 'ubuntu': 'Linux', 'debian': 'Linux', 'linux': 'Linux',
    'rhel': 'RHEL', 'sles': 'SUSE', 'windows': 'Windows',
}


class AwsPricing(object):
    def __init__(self, region=PRICE_REGION_LIST[0]):
        self._client = boto3.client('pricing', region_name=region)

    def get_service_codes(self):
        '''Retrieve all AWS service codes'''
        svcodeList = []
        args = {}
        while True:
            resp = self._client.describe_services(**args)
            svcodeList.extend([s['ServiceCode'] for s in resp['Services']])
            if 'NextToken' not in resp:
                break
            args['NextToken'] = resp['NextToken']
        return svcodeList

    def get_service_attributes(self, service_code='AmazonEC2'):
        '''Retrieve all attribute names for one service'''
        resp = self._client.describe_services(ServiceCode=service_code)['Services']
        return resp[0].get('AttributeNames')

    def get_attribute_values(self, service_code='AmazonEC2', attribute_name='instanceType'):
        '''Retrieve available values for an attribute'''
        valueList = []
        args = {'ServiceCode': service_code, 'AttributeName': attribute_name}
        while True:
            resp = self._client.get_attribute_values(**args)
            valueList.extend([a['Value'] for a in resp['AttributeValues']])
            if 'NextToken' not in resp:
                break
            args['NextToken'] = resp['NextToken']
        return valueList

    def ec2_monthly_cost(self, region, instype, os):
        '''获取EC2的月度成本(单位时间Month)'''
        if not os:
            return None
        pricelist = self._ec2_pricelist(region, instype, os)
        if isinstance(pricelist, str):
            return None
        currency = list(pricelist['pricePerUnit'].keys())[0]
        unitPrice = pricelist['pricePerUnit'].get(currency)
        if pricelist.get('unit') == 'Hrs':
            return {'value': float(unitPrice) * 730, 'currency': currency}
        return None

    def _ec2_pricelist(self, region, instype, os, soft='NA', option='OnDemand', tenancy='Shared'):
        '''获取EC2的价格列表(单位时间Hrs)'''
        insOS = OS_MAP.get(os, 'NA')
        result = self._client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'ServiceCode', 'Value': 'AmazonEC2'},
                {'Type': 'TERM_MATCH', 'Field': 'locationType', 'Value': 'AWS Region'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'UnusedCapacityReservation'},
                {'Type': 'TERM_MATCH', 'Field': 'RegionCode', 'Value': region},
                {'Type': 'TERM_MATCH', 'Field': 'marketoption', 'Value': option},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': tenancy},
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instype},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': insOS},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': soft},
            ],
        )
        if not result.get('PriceList'):
            return 'Unmatched parameters'
        prod = ast.literal_eval(result['PriceList'][0])
        terms = next(iter(prod['terms'].get(option).values()))
        return next(iter(terms['priceDimensions'].values()))

    def _extract_price(self, result_dict, option='OnDemand'):
        '''从产品结果中提取价格信息'''
        terms = next(iter(result_dict['terms'].get(option).values()))
        priceDimensions = terms['priceDimensions']
        priceList = next(iter(priceDimensions.values()))
        currency = next(iter(priceList['pricePerUnit']))
        value = priceList['pricePerUnit'].get(currency)
        return priceList, currency, value, terms

    def get_product_instance(self, region, instance_type, operation, option='OnDemand', tenancy='Shared'):
        '''Get EC2 Instance Attributes and ListPrice [unit: Month]'''
        result = self._client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'locationType', 'Value': 'AWS Region'},
                {'Type': 'TERM_MATCH', 'Field': 'ServiceCode', 'Value': 'AmazonEC2'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'UnusedCapacityReservation'},
                {'Type': 'TERM_MATCH', 'Field': 'RegionCode', 'Value': region},
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'marketoption', 'Value': option},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': tenancy},
                {'Type': 'TERM_MATCH', 'Field': 'operation', 'Value': operation},
            ],
        )
        if len(result.get('PriceList')) != 1:
            raise ValueError('Unmatched parameter values')

        resultDict = ast.literal_eval(result['PriceList'][0])
        attr = resultDict['product']['attributes']
        priceList, currency, value, terms = self._extract_price(resultDict, option)
        priceList.update({
            'unit': 'Month',
            'pricePerUnit': {'currency': currency, 'value': float(value) * 730},
            'effectiveDate': terms['effectiveDate'],
        })
        return {
            'productMeta': {
                'instanceFamily': attr['instanceFamily'],
                'currentGeneration': attr['currentGeneration'],
                'introduceUrl': INSTANCE_TYPE_URL + instance_type.split('.')[0],
                'regionCode': attr['regionCode'],
                'location': attr['location'],
            },
            'hardwareSpecs': {
                'physicalProcessor': attr['physicalProcessor'],
                'clockSpeed': attr.get('clockSpeed'),
                'processorArchitecture': attr['processorArchitecture'],
                'vcpu': attr['vcpu'],
                'memory': attr['memory'],
                'networkPerformance': attr['networkPerformance'],
                'gpu': attr.get('gpu'),
            },
            'softwareSpecs': {
                'operatingSystem': attr['operatingSystem'],
                'preInstalledSw': attr['preInstalledSw'],
                'licenseModel': attr['licenseModel'],
            },
            'listPrice': priceList,
        }

    def get_product_volume(self, region, volume_type, volume_size, option='OnDemand'):
        '''Get EBS Volume Attributes and ListPrice [unit: GB-Mo]'''
        result = self._client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'locationType', 'Value': 'AWS Region'},
                {'Type': 'TERM_MATCH', 'Field': 'ServiceCode', 'Value': 'AmazonEC2'},
                {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage'},
                {'Type': 'TERM_MATCH', 'Field': 'RegionCode', 'Value': region},
                {'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_type},
            ],
        )
        if len(result.get('PriceList')) != 1:
            raise ValueError('Unmatched parameters')

        resultDict = ast.literal_eval(result['PriceList'][0])
        attr = resultDict['product']['attributes']
        priceList, currency, value, terms = self._extract_price(resultDict, option)
        priceList.update({
            'unit': 'Month',
            'pricePerUnit': {'currency': currency, 'value': float(value) * float(volume_size)},
            'effectiveDate': terms['effectiveDate'],
        })
        return {
            'productMeta': {
                'volumeType': attr['volumeType'],
                'location': attr['location'],
                'storageMedia': attr['storageMedia'],
                'introduceUrl': '%s#%s' % (VOLUME_TYPE_URL, volume_type),
            },
            'productSpecs': {
                'maxThroughputvolume': attr['maxThroughputvolume'],
                'maxIopsvolume': attr.get('maxIopsvolume'),
                'maxVolumeSize': attr.get('maxVolumeSize'),
                'maxIopsBurstPerformance': attr.get('maxIopsBurstPerformance'),
            },
            'listPrice': priceList,
        }
