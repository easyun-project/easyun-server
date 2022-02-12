"""
  @module:  Dashboard lambda
  @desc:    抓取所有数据中心的块存储(EBS)数据并写入ddb
  @auth:    aleck
"""

import boto3
import json
import datetime
from dateutil.tz import tzlocal

Deploy_Region = 'us-east-1'
This_Region = 'us-east-1'
DC_List_Table = 'easyun-inventory-summary'

# 从ddb获取当前datacenter列表
def get_dcList():
    resource_ddb = boto3.resource('dynamodb', region_name= Deploy_Region)    
    table = resource_ddb.Table(DC_List_Table)
    dcList = table.get_item(
        Key={'dcName': 'all'}
    )['Item']['dcList']
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
            'diskID': d['VolumeId'],
            'tagName': nameTag,
            'volumeType': d['VolumeType'],
            'totalSize': d['Size'],
#             'usedSize': none,
            'diskIops': d.get('Iops'),
            'diskThruput': d.get('Throughput'),
            'diskState': d['State'],
            'attachSvr': attachSvr,
            'attachPath': attachPath,
            'diskType': diskType,
            'diskEncrypt': d['Encrypted'],
            'diskAz': d['AvailabilityZone'],
            'createDate': d['CreateTime'].isoformat(),
        }
        diskList.append(disk)    
    return diskList

# 在lambda_handle() 调用以上方法   
def lambda_handler(event, context):
    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table('easyun-inventory-stblock')    
    dcList = get_dcList()

    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = This_Region )

    for dc in dcList:
        diskInvt = list_disks(dc)
        diskItem={
            'dcName': dc,
            'dcInventory': diskInvt
        }
        table.put_item(Item = diskItem)    

    resp = {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }

    return resp