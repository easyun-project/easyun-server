# -*- coding: utf-8 -*-
"""
  @module:  AWS Service Quotas
  @desc:    Define basic attributes and functions for Service-quotas API.  
  @auth:    aleck
"""
import boto3


class ServiceQuotas(object):
    def __init__(self, region='us-east-1'):
        self._client = boto3.client('service-quotas', region_name=region)


    def get_all_service_codes(self):
        '''Retrieve all AWS service codes

        return example:
        [        
            {'ServiceCode': 'vpc', 'ServiceName': 'Amazon Virtual Private Cloud (Amazon VPC)'},
            {'ServiceCode': 'ec2', 'ServiceName': 'Amazon Elastic Compute Cloud (Amazon EC2)'},
            {'ServiceCode': 'ebs', 'ServiceName': 'Amazon Elastic Block Store (Amazon EBS)'}
        ]
        '''
        try:
            args = {}
            serviceList = []
            while True:
                resp = self._client.list_services(**args)
                for s in resp['Services']:
                    serviceList.append(s)
                
                if 'NextToken' not in resp:
                    break
                args['NextToken'] = resp['NextToken']

            return serviceList
        except Exception as ex:
            return str(ex)


    def list_service_quotas(self, service_code):
        '''Retrieve all AWS service quotas

        return example:
        [        
            {'quotaCode': 'L-3819A6DF', 'quotaName': 'All G and VT Spot Instance Requests', 'quotaValue': 64.0}
            {'quotaCode': 'L-6DA43717', 'quotaName': 'Attachments per VPC', 'quotaValue': 5.0}
            {'quotaCode': 'L-7029FAB6', 'quotaName': 'Virtual private gateways per region', 'quotaValue': 5.0}
        ]
        '''
        try:
            args = {
                'ServiceCode':service_code,
            }
            quotaList = []
            while True:
                resp = self._client.list_service_quotas(**args)
                for q in resp['Quotas']:
                    item={
                        'quotaCode':q['QuotaCode'],
                        'quotaName':q['QuotaName'],
                        'quotaValue':q['Value'],
                        'quotaUnit':q['Unit'],
                        'isAdjustable':q['Adjustable'],
                        'isGlobalQuota':q['GlobalQuota']                        
                    }
                    quotaList.append(item)
                
                if 'NextToken' not in resp:
                    break
                args['NextToken'] = resp['NextToken']

            return quotaList

        except Exception as ex:
            return str(ex)    


    def get_service_quotas(self, service_code, quota_codes:list):
        '''Retrieve multi service quotas' info'''
        try:
            quotasResp = self.list_service_quotas(service_code)
            quotaList = [ q for q in quotasResp if q['quotaCode'] in quota_codes ]
            return quotaList

        except Exception as ex:
            return str(ex)


    def get_service_quota(self, service_code, quota_code):
        '''Retrieve one service quota's info'''
        try:
            resp = self._client.get_service_quota(
                ServiceCode=service_code,
                QuotaCode=quota_code
            )['Quota']
            quotaItem = {
                # 'quotaCode':resp['QuotaCode'],
                'quotaName':resp['QuotaName'],
                'quotaValue':resp['Value'],
                'quotaUnit':resp['Unit'],
                'isAdjustable':resp['Adjustable'],
                'isGlobalQuota':resp['GlobalQuota']
            }
            return quotaItem

        except Exception as ex:
            return str(ex)


    def get_quota_value(self, service_code, quota_code):
        '''Retrieve one service quota's value'''
        try:
            resp = self._client.get_service_quota(
                ServiceCode=service_code,
                QuotaCode=quota_code
            )['Quota']
            return resp['Value']

        except Exception as ex:
            return str(ex)

