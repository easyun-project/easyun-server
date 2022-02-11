"""
  @module:  Dashboard lambda
  @desc:    抓取所有数据中心的服务器(EC2)数据并写入ddb
  @auth:    aleck, xdq
"""

import json
import boto3
from decimal import Decimal
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

# 获取指定 datacenter 的服务器列表(ec2)
def list_servers(dcName):
    instance_list = []
    resource_ec2 = boto3.resource('ec2', region_name=this_region)
    instacnes = resource_ec2.instances.filter(
        Filters=[
            {'Name': 'tag:Flag', 'Values': [dcName]}
        ])
    client_ec2 = boto3.client('ec2', region_name=this_region)
    for instance in instacnes:
        for tag in instance.tags:
            if 'Name' in tag['Key']:
                name = tag['Value']
        instance_type = instance.instance_type
        ebs_size = 0
        for disk in instance.block_device_mappings:
            ebs_id = disk['Ebs']['VolumeId']
            ebs_size = ebs_size + resource_ec2.Volume(ebs_id).size
        # memory
        ins_type = client_ec2.describe_instance_types(InstanceTypes=[instance.instance_type])
        ram = ins_type['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']
        ice = {
            'serverId':instance.instance_id,
            'serverName': name,
            'serverType': instance_type,
            'serverState': instance.state['Name'],
            'privateIp': instance.private_ip_address,
            'publicIp': instance.public_ip_address or None,
            'launchTime': str(instance.launch_time),
            'serverVcpu': instance.cpu_options["CoreCount"],
            'serverAvailabilityZone': instance.placement["AvailabilityZone"],
            'serverOs': resource_ec2.Image(instance.image_id).platform_details,
            'serverRam': Decimal(ram / 1024),
            'serverStorage': ebs_size
        }
        instance_list.append(ice)
    return instance_list


# 在lambda_handle() 调用以上方法
def lambda_handler(event, context):
    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table("easyun-inventory-server")
    dcList = get_dcList()
    for dc in dcList:
        serverInvt = list_servers(dc)
        metricItem = {
            'dcName': dc,
            'serverInventory': serverInvt
        }
        table.put_item(Item=metricItem)


# 在lambda_handle() 调用以上方法   
def lambda_handler(event, context):
    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table('easyun-inventory-server')    
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
