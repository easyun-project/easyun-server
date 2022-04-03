# -*- coding: utf-8 -*-
"""
  @module:  AWS region attributes
  @desc:    Define basic attributes of AWS EC2 in this file.  
  @auth:    aleck
"""
from easyun.libs.utils import load_json_config




'''AWS Region 列表 (26)'''
AWS_Regions = load_json_config('aws_region')


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



'''
AWS API Service endpoint
'''
#The Cost Explorer API provides the following endpoint:
# Global Region：
# https://ce.us-east-1.amazonaws.com
# GCR Region:
# https://ce.cn-northwest-1.amazonaws.com.cn

def query_ce_region(account_type):
    if account_type == 'global':
        ceRegion = 'us-east-1' 
    elif account_type == 'gcr':
        ceRegion = 'cn-northwest-1'
    else:
        ceRegion = None
    return ceRegion
