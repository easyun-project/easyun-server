# -*- coding: utf-8 -*-
"""
  @module:  The API Wrapper Module
  @desc:    AWS SDK Boto3 Client and Resource Wrapper.  
  @auth:    
"""
import ast
import boto3


INSTANCE_TYPE_URL = 'https://aws.amazon.com/cn/ec2/instance-types/'
VOLUME_TYPE_URL = 'https://aws.amazon.com/cn/ebs/volume-types/'


# SDK: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html
class AwsPricing(object):
    def __init__(self, region='ap-south-1'):
        self._client = boto3.client('pricing', region_name=region)

    # Pricing.Client.describe_services
    def get_service_codes(self):
        '''Retrieve all AWS service codes'''
        try:
            svcodeList = []
            describe_args = {}
            while True:
                describe_result = self._client.describe_services(
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
            return {'count': len(svcodeList), 'data': svcodeList}
        except Exception as ex:
            # logger.error(f"{self.__class__.__name__} exec failed. Error: {ex}'")
            return {self.__class__.__name__: str(ex)}

    def get_service_attributes(self, service_code='AmazonEC2'):
        '''Retrieve all attribute names for one service'''
        try:
            describe_result = self._client.describe_services(
                ServiceCode=service_code,
            )['Services']
            attrList = describe_result[0].get('AttributeNames')
            return {'count': len(attrList), 'data': attrList}
        except Exception as ex:
            # logger.error(f"{self.__class__.__name__} exec failed. Error: {ex}'")
            return {self.__class__.__name__: str(ex)}

    def get_attribute_values(
        self, service_code='AmazonEC2', attribute_name='instanceType'
    ):
        '''Retrieve available values for an attribute'''
        try:
            valueList = []
            describe_args = {
                'ServiceCode': service_code,
                'AttributeName': attribute_name,
            }
            while True:
                response = self._client.get_attribute_values(**describe_args)
                valueList.extend([a['Value'] for a in response['AttributeValues']])
                if 'NextToken' not in response:
                    break
                describe_args['NextToken'] = response['NextToken']
            return {'count': len(valueList), 'data': valueList}
        except Exception as ex:
            # logger.error(f"{self.__class__.__name__} exec failed. Error: {ex}'")
            return {self.__class__.__name__: str(ex)}

    def get_product_instance(
        self, region, instance_type, operation, option='OnDemand', tenancy='Shared'
    ):
        '''Get EC2 Instance Attributes and ListPrice [unit: Month]'''
        try:
            result = self._client.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'locationType',
                        'Value': 'AWS Region',
                    },
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'ServiceCode',
                        'Value': 'AmazonEC2',
                    },
                    # {'Type': 'TERM_MATCH', 'Field': 'productFamily','Value': 'Compute Instance'},
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'capacitystatus',
                        'Value': 'UnusedCapacityReservation',
                    },
                    {'Type': 'TERM_MATCH', 'Field': 'RegionCode', 'Value': region},
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'instanceType',
                        'Value': instance_type,
                    },
                    {'Type': 'TERM_MATCH', 'Field': 'marketoption', 'Value': option},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': tenancy},
                    {'Type': 'TERM_MATCH', 'Field': 'operation', 'Value': operation},
                    # {'Type': 'TERM_MATCH', 'Field': 'operatingSystem','Value': os},
                    # {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw','Value': soft},
                ],
            )
            # 如果返回条目不唯一则说明给的参数值异常
            if len(result.get('PriceList')) != 1:
                raise ValueError('Unmatched parameter values')

            # 通过 ast.literal_eval()函数 将字符串转为字典
            resultDict = ast.literal_eval(result['PriceList'][0])
            # 获取属性值并进行归类
            attrList = resultDict['product']['attributes']
            productMeta = {
                'instanceFamily': attrList['instanceFamily'],
                'currentGeneration': attrList['currentGeneration'],
                'introduceUrl': INSTANCE_TYPE_URL + instance_type.split('.')[0],
                'regionCode': attrList['regionCode'],
                'location': attrList['location'],
                'tenancy': attrList['tenancy'],
                'capacitystatus': attrList['capacitystatus'],
                'usagetype': attrList['usagetype'],
                'instancesku': attrList['instancesku'],
                'operation': attrList['operation'],
                'normalizationSizeFactor': attrList['normalizationSizeFactor'],
                'ecu': attrList['ecu'],
            }
            hardwareSpecs = {
                'physicalProcessor': attrList['physicalProcessor'],
                'clockSpeed': attrList.get('clockSpeed'),
                'processorArchitecture': attrList['processorArchitecture'],
                'vcpu': attrList['vcpu'],
                'memory': attrList['memory'],
                'dedicatedEbsThroughput': attrList['dedicatedEbsThroughput'],
                'networkPerformance': attrList['networkPerformance'],
                'gpu': attrList.get('gpu'),
            }
            softwareSpecs = {
                'operatingSystem': attrList['operatingSystem'],
                'preInstalledSw': attrList['preInstalledSw'],
                'licenseModel': attrList['licenseModel'],
            }
            instanceSotrage = {
                'volumeType': 'Instance Store',
                'description': attrList['storage'],
            }
            productFeature = {
                'intelTurboAvailable': attrList['intelTurboAvailable'],
                'vpcnetworkingsupport': attrList['vpcnetworkingsupport'],
                'enhancedNetworkingSupported': attrList['enhancedNetworkingSupported'],
                'classicnetworkingsupport': attrList['classicnetworkingsupport'],
                'intelAvx2Available': attrList['intelAvx2Available'],
                'intelAvxAvailable': attrList['intelAvxAvailable'],
                'processorFeatures': attrList.get('processorFeatures'),
            }

            # 提取价格信息
            terms = next(iter(resultDict['terms'].get(option).values()))
            priceDimensions = terms['priceDimensions']
            priceList = next(iter(priceDimensions.values()))
            # 提取单位价格和币种
            currency = next(iter(priceList['pricePerUnit']))
            value = priceList['pricePerUnit'].get(currency)
            # 换算为月度费用并转换格式
            priceFormat = {
                'unit': 'Month',
                'pricePerUnit': {
                    'currency': currency,
                    # 参考AWS做法按每月730h计算
                    'value': float(value) * 730,
                },
                'effectiveDate': terms['effectiveDate'],
            }
            priceList.update(priceFormat)

            prdInstance = {
                'productMeta': productMeta,
                'hardwareSpecs': hardwareSpecs,
                'softwareSpecs': softwareSpecs,
                'instanceSotrage': instanceSotrage,
                'productFeature': productFeature,
                'listPrice': priceList,
            }
            return prdInstance

        except Exception as ex:
            # logger.error(f"{self.__class__.__name__} exec failed. Error: {ex}'")
            return {self.__class__.__name__: str(ex)}

    def get_product_volume(self, region, volume_type, volume_size, option='OnDemand'):
        '''Get EBS Volume Attributes and ListPrice [unit: GB-Mo]'''
        try:
            result = self._client.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'locationType',
                        'Value': 'AWS Region',
                    },
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'ServiceCode',
                        'Value': 'AmazonEC2',
                    },
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'productFamily',
                        'Value': 'Storage',
                    },
                    {'Type': 'TERM_MATCH', 'Field': 'RegionCode', 'Value': region},
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'volumeApiName',
                        'Value': volume_type,
                    },
                ],
            )
            # 如果返回条目不唯一则说明给的参数值异常
            if len(result.get('PriceList')) != 1:
                raise ValueError('Unmatched parameters')

            # 通过 ast.literal_eval()函数 将字符串转为字典
            resultDict = ast.literal_eval(result['PriceList'][0])
            # 获取属性值并进行归类
            attrList = resultDict['product']['attributes']

            productMeta = {
                'volumeType': attrList['volumeType'],
                'location': attrList['location'],
                'storageMedia': attrList['storageMedia'],
                'introduceUrl': '%s#%s' % (VOLUME_TYPE_URL, volume_type),
                'usagetype': attrList['usagetype'],
            }
            productSpecs = {
                'maxThroughputvolume': attrList['maxThroughputvolume'],
                'maxIopsvolume': attrList.get('maxIopsvolume'),
                'maxVolumeSize': attrList.get('maxVolumeSize'),
                'maxIopsBurstPerformance': attrList.get('maxIopsBurstPerformance'),
            }
            #             volumeList = {
            #                 'volumeType': volume_type,
            #                 'volumeSzize': volume_size
            #             }
            # 提取价格信息
            terms = next(iter(resultDict['terms'].get(option).values()))
            priceDimensions = terms['priceDimensions']
            priceList = next(iter(priceDimensions.values()))
            # 提取单位价格和币种
            currency = next(iter(priceList['pricePerUnit']))
            value = priceList['pricePerUnit'].get(currency)
            # 换算为对应容量的月度费用并转换格式
            priceFormat = {
                'unit': 'Month',
                'pricePerUnit': {
                    'currency': currency,
                    'value': float(value) * float(volume_size),
                },
                'effectiveDate': terms['effectiveDate'],
            }
            priceList.update(priceFormat)

            prdVolume = {
                'productMeta': productMeta,
                'productSpecs': productSpecs,
                #                 'volumeList':volumeList,
                'listPrice': priceList,
            }
            return prdVolume

        except Exception as ex:
            # logger.error(f"{self.__class__.__name__} exec failed. Error: {ex}'")
            return {self.__class__.__name__: str(ex)}
