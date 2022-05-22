"""
  @module:  Dashboard lambda function - Security Group
  @desc:    抓取所有数据中心-安全组(Security Group)数据并写入ddb
  @auth:    aleck
"""

import json
import boto3
import datetime
from dateutil.tz import tzlocal

Deploy_Region = 'us-east-1'
This_Region = 'us-east-1'
Inventory_Table = 'easyun-inventory-all'

# 从ddb获取当前datacenter列表
def get_dc_list():
    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table(Inventory_Table)
    dcList = table.get_item(
        Key={'dc_name': 'all', 'invt_type': 'dclist'}
    )['Item'].get('invt_list')
    return dcList


def list_secgroups(dcName):
    client_ec2 = boto3.client('ec2')

    sgs = client_ec2.describe_security_groups(
        Filters=[
            {
                'Name': 'tag:Flag', 'Values': [dcName]
            },             
        ]
    )['SecurityGroups']

    sgList = []
    for sg in sgs:
        # 获取Tag:Name
        nameTag = next((tag['Value'] for tag in sg.get('Tags') if tag["Key"] == 'Name'), None)            
        sgItem = {
            'sgId':sg['GroupId'],
            'tagName': nameTag,
            'sgName': sg['GroupName'],                
            'sgDesc':sg['Description'],
            'ibRulesNum':len(sg['IpPermissions']),                
            'obRulesNum':len(sg['IpPermissionsEgress']),
            # 'ibPermissions':sg['IpPermissions'],
            # 'obPermissions':sg['IpPermissionsEgress'] 
        }
        sgList.append(sgItem)
    return sgList


# 在lambda_handle() 调用以上方法
def lambda_handler(event, context):
    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = Deploy_Region)

    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table("easyun-inventory-secgroup")
    dcList = get_dc_list()

    for dc in dcList:
        invtList = list_secgroups(dc)
        newItem={
            'dcName': dc,
            'dcInventory': invtList
        }
        table.put_item(Item = newItem)    

    return {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }
