"""
  @module:  Dashboard lambda function
  @desc:    抓取所有数据中心-子网(Subnet)数据并写入ddb
  @auth:    aleck
"""

import json
import boto3
import datetime
from dateutil.tz import tzlocal

Deploy_Region = 'us-east-1'
this_region = 'us-east-1'
Inventory_Table = 'easyun-inventory-all'

# 从ddb获取当前datacenter列表
def get_dc_list():
    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table(Inventory_Table)
    dcList = table.get_item(
        Key={'dc_name': 'all', 'invt_type': 'dclist'}
    )['Item'].get('invt_list')
    return dcList


def get_subnet_type(subnet):
    '''判断subnet type是 public 还是 private'''
    # 偷个懒先仅以名称判断
    nameTag = next((tag['Value'] for tag in subnet.get('Tags') if tag["Key"] == 'Name'), None)
    if nameTag.lower().startswith('pub'):
        subnetType = 'public'
    elif nameTag.lower().startswith('pri'):
        subnetType = 'private'
    else:
        subnetType = None
    return subnetType


def list_subnets(dcName):
    client_ec2 = boto3.client('ec2')

    subnets = client_ec2.describe_subnets(
        Filters=[
            { 'Name': 'tag:Flag', 'Values': [dcName] },             
        ]
    )['Subnets']

    subnetList = []
    for subnet in subnets:
        # 获取Tag:Name
        nameTag = next((tag['Value'] for tag in subnet.get('Tags') if tag["Key"] == 'Name'), None)
        # 判断subnet type是 public 还是 private
        subnetType = get_subnet_type(subnet)
        subnetItem = {
            'tagName' : nameTag,
            'subnetType': subnetType,
            'subnetState':subnet['State'],
            'subnetId':subnet['SubnetId'],
            # 'vpcId':subnet['VpcId'],
            'azName':subnet['AvailabilityZone'],
            'cidrBlock':subnet['CidrBlock'],
            # 'cidrBlockv6':subnet['Ipv6CidrBlockAssociationSet'][0].get('Ipv6CidrBlock'),
            'cidrBlockv6':None,
            'avlipNum':subnet['AvailableIpAddressCount'],
            'isMappubip':subnet['MapPublicIpOnLaunch']
        }
        subnetList.append(subnetItem)
    return subnetList


# 在lambda_handle() 调用以上方法
def lambda_handler(event, context):
    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = Deploy_Region)

    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table("easyun-inventory-subnet")
    dcList = get_dc_list()
    for dc in dcList:
        invtList = list_subnets(dc)
        newItem={
            'dcName': dc,
            'dcInventory': invtList
        }
        table.put_item(Item = newItem)    

    return {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }
