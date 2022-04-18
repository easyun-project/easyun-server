# -*- coding: utf-8 -*-
"""
  @module:  Server (ec2) SDK Module
  @desc:    AWS SDK Boto3 EC2 Client and Resource Wrapper.  
  @auth:    
"""
import boto3


class EC2Server(object):
    def __init__(self):
        self._client = boto3.resource('ec2')
        self._resource = boto3.resource('ec2')

    #SDK: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html#Pricing.Client.describe_services
    def get_service_codes(self):
        '''Retrieve all AWS service codes'''
        try:
            svcodeList = []
            describe_args = {}
            while True:
                describe_result = self._boto3_client.describe_services(
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
            return {
                'count':len(svcodeList),
                'data':svcodeList
            }
        except Exception as ex:
            return '%s: %s' %(self.__class__.__name__ ,ex)
            