# -*- coding: utf-8 -*-
"""
  @module:  AWS Price Attributes
  @desc:    Define basic attributes and functions for AWS Price API.  
  @auth:    aleck
"""

import boto3
import ast

'''
AWS Price API Endpoint (both support GCR):
# https://api.pricing.us-east-1.amazonaws.com
# https://api.pricing.ap-south-1.amazonaws.com
'''
# Global Region: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-pelong.html
# GCR Region:  https://docs.amazonaws.cn/awsaccountbilling/latest/aboutv2/using-pelong.html
# AWS Price API only support us-east-1, ap-south-1
Price_Region_List = ['us-east-1','ap-south-1']


#SDK: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html#Pricing.Client.describe_services
def get_service_codes():
    '''Retrieve all AWS service codes'''
    try:
        client_price = boto3.client('pricing', region_name= Price_Region_List[0] )
        svcodeList = []
        describe_args = {}
        while True:
            describe_result = client_price.describe_services(
                **describe_args,
                # FormatVersion='string',
                # NextToken='string',
                # MaxResults=100
            )
            svcodeList.extend(
                [s['ServiceCode'] for s in describe_result['Services']]
            )
            if 'NextToken' not in describe_result:
                break
            describe_args['NextToken'] = describe_result['NextToken']
        return svcodeList
    except Exception as ex:
        return str(ex)


def get_service_attributes(service_code = 'AmazonEC2'):
    '''Retrieve all attribute names for one service'''
    try:
        client_price = boto3.client('pricing', region_name= Price_Region_List[0] )
        describe_result = client_price.describe_services(
            ServiceCode = service_code,
        )['Services']
        attrList = describe_result[0].get('AttributeNames')
        return attrList
    except Exception as ex:
        return str(ex)


def get_attribute_values(service_code = 'AmazonEC2', attribute_name = 'instanceType'):
    '''Retrieve available values for an attribute'''
    try:
        client_price = boto3.client('pricing', region_name= Price_Region_List[0] )
        valueList = []
        describe_args = {
            'ServiceCode' : service_code,
            'AttributeName' : attribute_name
        }
        while True:        
            response = client_price.get_attribute_values( **describe_args )
            valueList.extend(
                [a['Value'] for a in response['AttributeValues']]
            )
            if 'NextToken' not in response:
                break
            describe_args['NextToken'] = response['NextToken']
        return valueList
    except Exception:
        pass


'''
Define usage operation by platform.
platformDetails value indicates the operation of an Amazon EC2 instance.
url: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/billing-info-fields.html
'''
Platform_to_Operation = [
    {
        'platformDetails':'Linux/UNIX', 
        'usageOperation':'RunInstances',},
    {
        'platformDetails': 'Red Hat BYOL Linux',
        'usageOperation': 'RunInstances:00g0'},
    {
        'platformDetails': 'Red Hat Enterprise Linux',
        'usageOperation': 'RunInstances:0010'},
    {
        'platformDetails': 'Red Hat Enterprise Linux with HA',
        'usageOperation': 'RunInstances:1010'},
    {
        'platformDetails': 'Red Hat Enterprise Linux with SQL Server Standard and HA',
        'usageOperation': 'RunInstances:1014'},
    {
        'platformDetails': 'Red Hat Enterprise Linux with SQL Server Enterprise and HA',
        'usageOperation': 'RunInstances:1110'},
    {
        'platformDetails': 'Red Hat Enterprise Linux with SQL Server Standard',
        'usageOperation': 'RunInstances:0014'},
    {
        'platformDetails': 'Red Hat Enterprise Linux with SQL Server Web',
        'usageOperation': 'RunInstances:0210'},
    {
        'platformDetails': 'Red Hat Enterprise Linux with SQL Server Enterprise',
        'usageOperation': 'RunInstances:0110'},
    {
        'platformDetails': 'SQL Server Enterprise',
        'usageOperation': 'RunInstances:0100'},
    {
        'platformDetails': 'SQL Server Standard',
        'usageOperation': 'RunInstances:0004'},
    {
        'platformDetails': 'SQL Server Web', 
        'usageOperation': 'RunInstances:0200'},
    {
        'platformDetails': 'SUSE Linux', 
        'usageOperation': 'RunInstances:000g'},
    {
        'platformDetails': 'Windows', 
        'usageOperation': 'RunInstances:0002'},
    {
        'platformDetails': 'Windows BYOL', 
        'usageOperation': 'RunInstances:0800'},
    {
        'platformDetails': 'Windows with SQL Server Enterprise *',
        'usageOperation': 'RunInstances:0102'},
    {
        'platformDetails': 'Windows with SQL Server Standard',
        'usageOperation': 'RunInstances:0006'},
    {
        'platformDetails': 'Windows with SQL Server Web',
        'usageOperation': 'RunInstances:0202'}
]

'''OS Codes defined by Easyun'''
OS_Code_List = ['amzn2', 'ubuntu', 'debian', 'linux','rhel','sles','windows']


def ec2_monthly_cost(region, instype, os):
    '''获取EC2的月度成本(单位时间Month)'''
    if not os:
        return None
    try:
        pricelist = ec2_pricelist(region, instype, os)
        unit = pricelist.get('unit')
        currency = list(pricelist['pricePerUnit'].keys())[0]
        unitPrice = pricelist['pricePerUnit'].get(currency)
        if unit == 'Hrs':
            # 参考AWS做法按每月730h计算
            monthPrice = float(unitPrice)*730
        return {
            'value': monthPrice,
            'currency' : currency
        }
    except Exception as ex:
        return ex

# 获取实例价格功能实现部分
def ec2_pricelist(
        region, instype, os, 
        soft='NA', 
        option='OnDemand',
        tenancy='Shared'
    ):
    '''获取EC2的价格列表(单位时间Hrs)'''

    # 将传入的 os 匹配为 price api 支持的 operatingSystem
    if os in ['amzn2', 'ubuntu', 'debian', 'linux']:
        insOS = 'Linux'
    elif os == 'rhel':
        insOS = 'RHEL'
    elif os == 'sles':
        insOS = 'SUSE' 
    elif os == 'windows':
        insOS = 'Windows'
    else: 
        insOS = 'NA'

    try:
        client_price = boto3.client('pricing', region_name= Price_Region_List[0] )
        result = client_price.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'ServiceCode','Value': 'AmazonEC2'},
                {'Type': 'TERM_MATCH', 'Field': 'locationType','Value': 'AWS Region'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus','Value': 'UnusedCapacityReservation'},             
                {'Type': 'TERM_MATCH', 'Field': 'RegionCode','Value': region},
                {'Type': 'TERM_MATCH', 'Field': 'marketoption','Value': option},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy','Value': tenancy},
                {'Type': 'TERM_MATCH', 'Field': 'instanceType','Value': instype},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem','Value': insOS},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw','Value': soft},
            ],
        )
        # 通过 ast.literal_eval()函数 对字符串进行类型转换
        if not result.get('PriceList'):
            return 'Unmatched parameters'
        prod = ast.literal_eval(result['PriceList'][0])
        price1 = prod['terms'].get(option)  
        key1 = list(price1.keys())[0]
        price2 = price1[key1]['priceDimensions']
        key2 = list(price2.keys())[0]
        price3 = price2[key2]
        return price3
    except Exception as ex:
        return str(ex)
