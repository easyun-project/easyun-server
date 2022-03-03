# -*- coding: utf-8 -*-
"""
  @module:  AWS region attributes
  @desc:    Define basic attributes of AWS EC2 in this file.  
  @auth:    aleck
"""


'''AWS Region 列表 (26)'''
AWS_Regions = [
    {
        "regionCode": "us-east-1",
        "countryCode": "USA",
        "regionName": {
            "eng": "US East (N. Virginia)",
            "chs": "美国东部（弗吉尼亚北部）"
        }
    },
    {
        "regionCode": "us-east-2",
        "countryCode": "USA",
        "regionName": {
            "eng": "US East (Ohio)",
            "chs": "美国东部（俄亥俄）"
        }
    },
    {
        "regionCode": "us-west-1",
        "countryCode": "USA",
        "regionName": {
            "eng": "US West (Northern California)",
            "chs": "美国西部（加利福尼亚北部）"
        }
    },
    {
        "regionCode": "us-west-2",
        "countryCode": "USA",
        "regionName": {
            "eng": "US West (Oregon)",
            "chs": "美国西部（俄勒冈）"
        }
    },
    {
        "regionCode": "af-south-1",
        "countryCode": "ZAF",
        "regionName": {
            "eng": "Africa (Cape Town)",
            "chs": " 非洲（开普敦）"
        }
    },
    {
        "regionCode": "ap-east-1",
        "countryCode": "HKG",
        "regionName": {
            "eng": "Asia Pacific (Hong Kong)",
            "chs": "亚太地区（香港）"
        }
    },
    {
        "regionCode": "ap-south-1",
        "countryCode": "IND",
        "regionName": {
            "eng": "Asia Pacific (Mumbai)",
            "chs": "亚太地区（孟买）"
        }
    },
    {
        "regionCode": "ap-northeast-3",
        "countryCode": "JPN",
        "regionName": {
            "eng": "Asia Pacific (Osaka)",
            "chs": "亚太地区（大阪）"
        }
    },
    {
        "regionCode": "ap-northeast-2",
        "countryCode": "KOR",
        "regionName": {
            "eng": "Asia Pacific (Seoul)",
            "chs": "亚太地区（首尔）"
        }
    },
    {
        "regionCode": "ap-southeast-1",
        "countryCode": "SGP",
        "regionName": {
            "eng": "Asia Pacific (Singapore)",
            "chs": "亚太地区（新加坡）"
        }
    },
    {
        "regionCode": "ap-southeast-2",
        "countryCode": "AUS",
        "regionName": {
            "eng": "Asia Pacific (Sydney)",
            "chs": "  亚太地区（悉尼）"
        }
    },
    {
        "regionCode": "ap-southeast-3",
        "countryCode": "IDN",
        "regionName": {
            "eng": "Asia Pacific (Jakarta)",
            "chs": " 亚太地区（雅加达）"
        }
    },
    {
        "regionCode": "ap-northeast-1",
        "countryCode": "JPN",
        "regionName": {
            "eng": "Asia Pacific (Tokyo)",
            "chs": "亚太地区（东京）"
        }
    },
    {
        "regionCode": "ca-central-1",
        "countryCode": "CAN",
        "regionName": {
            "eng": "Canada (Central)",
            "chs": "加拿大（中部）"
        }
    },
    {
        "regionCode": "eu-central-1",
        "countryCode": "DEU",
        "regionName": {
            "eng": "Europe (Frankfurt)",
            "chs": "欧洲（法兰克福）"
        }
    },
    {
        "regionCode": "eu-west-1",
        "countryCode": "IRL",
        "regionName": {
            "eng": "Europe (Ireland)",
            "chs": "欧洲（爱尔兰）"
        }
    },
    {
        "regionCode": "eu-west-2",
        "countryCode": "GBR",
        "regionName": {
            "eng": "Europe (London)",
            "chs": "欧洲（伦敦）"
        }
    },
    {
        "regionCode": "eu-south-1",
        "countryCode": "ITA",
        "regionName": {
            "eng": "Europe (Milan)",
            "chs": "欧洲（米兰）"
        }
    },
    {
        "regionCode": "eu-west-3",
        "countryCode": "FRA",
        "regionName": {
            "eng": "Europe (Paris)",
            "chs": "欧洲（巴黎）"
        }
    },
    {
        "regionCode": "eu-north-1",
        "countryCode": "SWE",
        "regionName": {
            "eng": "Europe (Stockholm)",
            "chs": "欧洲（斯德哥尔摩）"
        }
    },
    {
        "regionCode": "me-south-1",
        "countryCode": "BHR",
        "regionName": {
            "eng": "Middle East (Bahrain)",
            "chs": "中东（巴林）"
        }
    },
    {
        "regionCode": "sa-east-1",
        "countryCode": "BRA",
        "regionName": {
            "eng": "South America (Sao Paulo)",
            "chs": "南美洲（圣保罗）"
        }
    },
    {
        "regionCode": "us-gov-east-1",
        "countryCode": "USA",
        "regionName": {
            "eng": "AWS GovCloud (US-East)",
            "chs": "AWS GovCloud（美国东部）"
        }
    },
    {
        "regionCode": "us-gov-west-1",
        "countryCode": "USA",
        "regionName": {
            "eng": "AWS GovCloud (US-West)",
            "chs": "  AWS GovCloud（美国西部）"
        }
    },
    {
        "regionCode": "cn-north-1",
        "countryCode": "CHN",
        "regionName": {
            "eng": "China (Beijing)",
            "chs": "  中国（北京）"
        }
    },
    {
        "regionCode": "cn-northwest-1",
        "countryCode": "CHN",
        "regionName": {
            "eng": "China (Ningxia)",
            "chs": " 中国（宁夏）"
        }
    }
]


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
