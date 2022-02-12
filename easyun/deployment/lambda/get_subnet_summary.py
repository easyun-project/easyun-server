"""
  @module:  Dashboard lambda - Subnet
  @desc:    抓取所有数据中心的子网(Subnet)数据并写入ddb
  @auth:    qian
"""


import boto3
import json
from typing import Dict
from collections import defaultdict

meta_region ={
    "us-east-1":{
        
        "code": "USA",
        "name": {
            "Eng": "US East (N. Virginia)",
            "Chs": "美国东部（弗吉尼亚北部）"
        }
    },
    "us-east-2":{
        "code": "USA",
        "name": {
            "Eng": "US East (Ohio)",
            "Chs": "美国东部（俄亥俄）"
        }
    },
    "us-west-1":{
        "code": "USA",
        "name": {
            "Eng": "US West (Northern California)",
            "Chs": "美国西部（加利福尼亚北部）"
        }
    },
    "us-west-2":{
        "code": "USA",
        "name": {
            "Eng": "US West (Oregon)",
            "Chs": "美国西部（俄勒冈）"
        }
    },
    "af-south-1":{
        "code": "ZAF",
        "name": {
            "Eng": "Africa (Cape Town)",
            "Chs": " 非洲（开普敦）"
        }
    },
    "ap-east-1":{
        "code": "HKG",
        "name": {
            "Eng": "Asia Pacific (Hong Kong)",
            "Chs": "亚太地区（香港）"
        }
    },
    "ap-south-1":{
        "code": "IND",
        "name": {
            "Eng": "Asia Pacific (Mumbai)",
            "Chs": "亚太地区（孟买）"
        }
    },
    "ap-northeast-3": {
        "code": "JPN",
        "name": {
            "Eng": "Asia Pacific (Osaka)",
            "Chs": "亚太地区（大阪）"
        }
    },
    "ap-northeast-2":{
        "code": "KOR",
        "name": {
            "Eng": "Asia Pacific (Seoul)",
            "Chs": "亚太地区（首尔）"
        }
    },
    "ap-southeast-1": {
        "code": "SGP",
        "name": {
            "Eng": "Asia Pacific (Singapore)",
            "Chs": "亚太地区（新加坡）"
        }
    },
    "ap-southeast-2":{
        "code": "AUS",
        "name": {
            "Eng": "Asia Pacific (Sydney)",
            "Chs": "  亚太地区（悉尼）"
        }
    },
    "ap-southeast-3":{
        
        "code": "IDN",
        "name": {
            "Eng": "Asia Pacific (Jakarta)",
            "Chs": " 亚太地区（雅加达）"
        }
    },
    "ap-northeast-1":{
        "code": "JPN",
        "name": {
            "Eng": "Asia Pacific (Tokyo)",
            "Chs": "亚太地区（东京）"
        }
    },
    "ca-central-1":{
        "code": "CAN",
        "name": {
            "Eng": "Canada (Central)",
            "Chs": "加拿大（中部）"
        }
    },
    "eu-central-1":{
        "code": "DEU",
        "name": {
            "Eng": "Europe (Frankfurt)",
            "Chs": "欧洲（法兰克福）"
        }
    },
    "eu-west-1":{
        "code": "IRL",
        "name": {
            "Eng": "Europe (Ireland)",
            "Chs": "欧洲（爱尔兰）"
        }
    },
    "eu-west-2":{
        "code": "GBR",
        "name": {
            "Eng": "Europe (London)",
            "Chs": "欧洲（伦敦）"
        }
    },
    "eu-south-1":{
        "code": "ITA",
        "name": {
            "Eng": "Europe (Milan)",
            "Chs": "欧洲（米兰）"
        }
    },
    "eu-west-3":{
        "code": "FRA",
        "name": {
            "Eng": "Europe (Paris)",
            "Chs": "欧洲（巴黎）"
        }
    },
    "eu-north-1":{
        "code": "SWE",
        "name": {
            "Eng": "Europe (Stockholm)",
            "Chs": "欧洲（斯德哥尔摩）"
        }
    },
    "me-south-1":{
        "code": "BHR",
        "name": {
            "Eng": "Middle East (Bahrain)",
            "Chs": "中东（巴林）"
        }
    },
    "sa-east-1":{
        "code": "BRA",
        "name": {
            "Eng": "South America (Sao Paulo)",
            "Chs": "南美洲（圣保罗）"
        }
    },
    "us-gov-east-1":{
        "code": "USA",
        "name": {
            "Eng": "AWS GovCloud (US-East)",
            "Chs": "AWS GovCloud（美国东部）"
        }
    },
    "us-gov-west-1":{
        "code": "USA",
        "name": {
            "Eng": "AWS GovCloud (US-West)",
            "Chs": "  AWS GovCloud（美国西部）"
        }
    },
    "cn-north-1":{
        "code": "CHN",
        "name": {
            "Eng": "China (Beijing)",
            "Chs": "  中国（北京）"
        }
    },
    "cn-northwest-1":{
        "code": "CHN",
        "name": {
            "Eng": "China (Ningxia)",
            "Chs": " 中国（宁夏）"
        }
    }
}

def get_subnet_summary(vpc: str, dc: str, meta_region: Dict) -> Dict:
    client = boto3.client('ec2')

    subnet_list = client.describe_subnets(
        Filters=[
            {
                'Name': 'vpc-id', 'Values': [vpc]
            },
            {
                'Name': 'state', 'Values': ['available']
            },
            {
                'Name': 'tag:Flag', 'Values': [dc]
            },
        ],
    )
    res = defaultdict(list)

    for subnet in subnet_list['Subnets']:
        for k, v in subnet.items():
            if k == 'AvailabilityZone':
                AvailabilityZone = v
            elif k == 'SubnetId':
                SubnetId = v
        res[AvailabilityZone].append(SubnetId)
        del AvailabilityZone, SubnetId
    
    return [{**{'vpc':vpc,'dc':dc, 'az': k, "empty": int(len(v) == 0), 'subnet': len(v), 'region': k[:-1]}, **meta_region[k[:-1]]}
            for k, v in res.items()]


def create_summary_table(tableName, dynamodb):
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'az',
                'KeyType': 'HASH'
            },
                        {
                'AttributeName': 'vpc',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'az',
                'AttributeType': 'S'
            },
                        {
                'AttributeName': 'vpc',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }
    )

    return "Table status:", table.table_status


def create_summary(table, summary):
    table.put_item(Item=summary)



def lambda_handler(event, context):
    this_vpc = 'vpc-057f0e3d715c24147'
    this_dc = 'Easyun'
    tableName = 'dashboard-summary'

    subnet_summaries = get_subnet_summary(vpc=this_vpc, dc=this_dc, meta_region=meta_region)

    dynamodb = boto3.resource('dynamodb')
    table_names = [table.name for table in dynamodb.tables.all()]

    if tableName not in table_names:
        res_create_table = create_summary_table(tableName, dynamodb)

    table = dynamodb.Table(tableName)
    ress = []
    for summary in subnet_summaries:
        res = create_summary(table, summary)
        ress.append(res)
    response = {
        "statusCode": 200,
        "body": json.dumps(ress)
    }

    return response
