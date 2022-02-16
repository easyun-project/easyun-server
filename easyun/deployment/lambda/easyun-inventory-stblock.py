"""
  @module:  Dashboard lambda function
  @desc:    抓取所有数据中心的块存储(EBS)数据并写入ddb
  @auth:    aleck
"""

import boto3
import json
import datetime
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

# 通过instanceID 获取服务器 tag:Name     
def get_svr_name(insID):
    resource_ec2 = boto3.resource('ec2')
    server = resource_ec2.Instance(insID)
    nameTag = next((tag['Value'] for tag in server.tags if tag["Key"] == 'Name'), None)
    return nameTag

# 获取指定 datacenter 的 disk(volume)     
def list_disks(dcName):
    client_ec2 = boto3.client('ec2')
    volumeList = client_ec2.describe_volumes(
        Filters=[
            {'Name': 'tag:Flag', 'Values': [dcName]},
        ]
    )['Volumes']
    SystemDisk = ['/dev/xvda','/dev/sda1']
    diskList = []
    for d in volumeList:
        nameTag = next((tag['Value'] for tag in d['Tags'] if tag.get('Key') == 'Name'), None)
        attach = d.get('Attachments')
        if attach:
            attachPath = attach[0].get('Device')
            insId = attach[0].get('InstanceId')
            attachSvr = get_svr_name(insId)
        else:
            attachPath = ''
            attachSvr = ''
        
        diskType = 'system' if attachPath in SystemDisk else 'user'
        disk = {
            'volumeId': d['VolumeId'],
            'tagName': nameTag,
            'volumeType': d['VolumeType'],
            'volumeSize': d['Size'],
#             'usedSize': none,
            'volumeIops': d.get('Iops'),
            'volumeThruput': d.get('Throughput'),
            'volumeState': d['State'],
            'attachSvr': attachSvr,
            'attachPath': attachPath,
            'diskType': diskType,
            'isEncrypted': d['Encrypted'],
            'volumeAz': d['AvailabilityZone'],
            'createTime': d['CreateTime'].isoformat(),
        }
        diskList.append(disk)    
    return diskList

# 在lambda_handle() 调用以上方法   
def lambda_handler(event, context):
    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = Deploy_Region)

    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table('easyun-inventory-stblock')    
    dcList = get_dc_list()

    for dc in dcList:
        invtList = list_disks(dc)
        newItem={
            'dcName': dc,
            'dcInventory': invtList
        }
        table.put_item(Item = newItem)    

    return {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }
