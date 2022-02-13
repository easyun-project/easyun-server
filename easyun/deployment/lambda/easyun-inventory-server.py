"""
  @module:  Dashboard lambda function
  @desc:    抓取所有数据中心的服务器(EC2)数据并写入ddb
  @auth:    xdq, aleck
"""

import boto3
import json
import datetime
from decimal import Decimal
from dateutil.tz import tzlocal

Deploy_Region = 'us-east-1'
This_Region = 'us-east-1'
Inventory_Table = 'easyun-inventory-all'

# 从ddb获取当前datacenter列表
def get_dc_list():
    resource_ddb = boto3.resource('dynamodb', region_name= Deploy_Region) 
    table = resource_ddb.Table(Inventory_Table)
    dcList = table.get_item(
        Key={'dc_name': 'all', 'invt_type': 'dclist'}
    )['Item'].get('invt_list')
    return dcList

# 获取指定 datacenter 的服务器列表(ec2)
def list_servers(dcName):
    svrList = []
    client_ec2 = boto3.client('ec2')
    resource_ec2 = boto3.resource('ec2')
    svrIterator = resource_ec2.instances.filter(
        Filters=[
            {'Name': 'tag:Flag', 'Values': [dcName]},
        ])

    for s in svrIterator:
        # tag:name
        nameTag = next((tag['Value'] for tag in s.tags if tag["Key"] == 'Name'), None)
        # disk
        volumeSize = 0
        for disk in s.block_device_mappings:
            ebsId = disk['Ebs']['VolumeId']
            volumeSize += resource_ec2.Volume(ebsId).size
        # memory
        insType = client_ec2.describe_instance_types(InstanceTypes=[s.instance_type])
        ramSize = insType['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']
        svrItem = {
            'svrId' : s.id,
            'tagName': nameTag,
            'svrState' : s.state["Name"],
            'insType' : s.instance_type,
            'vpuNum' : s.cpu_options['CoreCount'],
            'ramSize' : Decimal(ramSize/1024),
            'volumeSize' : volumeSize, 
            'osName' : resource_ec2.Image(s.image_id).platform_details,               
            'azName' : resource_ec2.Subnet(s.subnet_id).availability_zone,
            'pubIp' : s.public_ip_address,
            'priIp' : s.private_ip_address,
            'launchTime': s.launch_time.isoformat()
        }
        svrList.append(svrItem)
    return svrList


# 在lambda_handle() 调用以上方法
def lambda_handler(event, context):
    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table("easyun-inventory-server")
    dcList = get_dc_list()

    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = This_Region )

    for dc in dcList:
        svrInvt = list_servers(dc)
        svrItem = {
            'dcName': dc,
            'dcInventory': svrInvt
        }
        table.put_item(Item = svrItem)

    return {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }
