# -*- coding: utf-8 -*-
"""
  @module:  AWS region attributes
  @desc:    Define basic attributes of AWS EC2 in this file.  
  @auth:    aleck
"""
import boto3
from easyun.libs.utils import load_json_config



'''AWS Region 列表 (26)'''
AWS_Regions = load_json_config('aws_region')

def get_region_codes(account_type='global'):
    if account_type == 'gcr':
        regionCodes = boto3._get_default_session().get_available_regions('ec2', 'aws-cn')
    else:
        regionCodes = boto3._get_default_session().get_available_regions('ec2')
    return regionCodes


def query_country_code(region):
    regionDict = next((r for r in AWS_Regions if r["regionCode"] == region), None)
    if regionDict:
        return regionDict["countryCode"]
    else:
        return None


def query_region_name(region):
    regionDict = next((r for r in AWS_Regions if r["regionCode"] == region), None)
    if regionDict:
        return regionDict['regionName'].get('eng')
    else:
        return None
