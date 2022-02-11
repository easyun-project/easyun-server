"""
  @module:  Dashboard lambda
  @desc:    抓取所有数据中心的服务器(EC2)数据并写入ddb
  @auth:    aleck
"""

import json
import boto3
import datetime
from dateutil.tz import tzlocal

deploy_region = 'us-east-1'
this_region = 'us-east-1'

# 从ddb获取当前datacenter列表
def get_dcList():
    resource_ddb = boto3.resource('dynamodb', region_name= deploy_region)    
    table = resource_ddb.Table('easyun-inventory-summary')
    dcList = table.get_item(
        Key={'dcName': 'all'}
    )['Item']['dcList']
    return dcList

# 通过instanceID 获取服务器 tag:Name     
def get_svr_name(insID):
    resource_ec2 = boto3.resource('ec2', region_name=this_region)
    server = resource_ec2.Instance(insID)
    nameTag = [tag['Value'] for tag in server.tags if tag['Key'] == 'Name']
    svrName = nameTag[0] if len(nameTag) else None
    return svrName

# 获取指定 datacenter 的 disk(volume)     
def list_disks(dcName):
    client_ec2 = boto3.client('ec2', region_name = this_region)
    volumeList = client_ec2.describe_volumes(
        Filters=[
            {
                'Name': 'tag:Flag',
                'Values': [dcName,]
            },
        ]
    )['Volumes']
    SystemDisk = ['/dev/xvda','/dev/sda1']
    diskList = []
    for d in volumeList:
        nameTag = [tag['Value'] for tag in d['Tags'] if tag.get('Key') == 'Name']
        attach = d['Attachments']
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
            'tagName': nameTag[0] if len(nameTag) else None,
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
    for dc in dcList:
        diskInvt = list_disks(dc)
        diskItem={
            'dcName': dc,
            'dcInventory': diskInvt
        }
        table.put_item(Item = diskItem)    

    return {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }