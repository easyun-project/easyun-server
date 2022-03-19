# -*- coding: utf-8 -*-
"""
  @module:  AWS Service Quotas
  @desc:    Define basic attributes and functions for Service-quotas API.  
  @auth:    aleck
"""

import boto3

def get_service_codes():
    '''Retrieve all AWS service codes

    return example:
    [        
        {'ServiceCode': 'vpc', 'ServiceName': 'Amazon Virtual Private Cloud (Amazon VPC)'},
        {'ServiceCode': 'ec2', 'ServiceName': 'Amazon Elastic Compute Cloud (Amazon EC2)'},
        {'ServiceCode': 'ebs', 'ServiceName': 'Amazon Elastic Block Store (Amazon EBS)'}
    ]
    '''
    try:
        client_sq = boto3.client('service-quotas')
        args = {}
        serviceList = []
        while True:
            resp = client_sq.list_services(**args)
            for s in resp['Services']:
                serviceList.append(s)
            
            if 'NextToken' not in resp:
                break
            args['NextToken'] = resp['NextToken']

        return serviceList
    except Exception as ex:
        return str(ex)


def get_service_quotas(svc_code):
    '''Retrieve all AWS service quotas

    return example:
    [        
        {'QuotaCode': 'L-3819A6DF', 'QuotaName': 'All G and VT Spot Instance Requests', 'QuotaValue': 64.0}
        {'QuotaCode': 'L-6DA43717', 'QuotaName': 'Attachments per VPC', 'QuotaValue': 5.0}
        {'QuotaCode': 'L-7029FAB6', 'QuotaName': 'Virtual private gateways per region', 'QuotaValue': 5.0}
    ]
    '''
    try:
        client_sq = boto3.client('service-quotas')
        args = {
            'ServiceCode':svc_code,
        }
        quotaList = []
        while True:
            resp = client_sq.list_service_quotas(**args)
            for q in resp['Quotas']:
                item={
                    'QuotaCode':q['QuotaCode'],
                    'QuotaName':q['QuotaName'],
                    'QuotaValue':q['Value']
                }
                quotaList.append(item)
            
            if 'NextToken' not in resp:
                break
            args['NextToken'] = resp['NextToken']

        return quotaList

    except Exception as ex:
        return str(ex)    


def get_quota_value(svc_code, quota_code):
    '''Retrieve service quota's value'''
    try:
        client_sq = boto3.client('service-quotas')
        resp = client_sq.get_service_quota(
            ServiceCode=svc_code,
            QuotaCode=quota_code
        )['Quota']
        return resp['Value']        

    except Exception as ex:
        return str(ex)           

