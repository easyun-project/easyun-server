"""
  @module:  Dashboard lambda function function
  @desc:    抓取所有数据中心的数据库(RDS)数据并写入ddb
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

# 获取指定 datacenter 的 database(rds instance)
def list_dbinstances(dcName):
    client_rds = boto3.client('rds')
    dbis = client_rds.describe_db_instances(
#     volumeList = client_rds.describe_db_clusters(
#         DBInstanceIdentifier='string',
#         Filters=[
#             { 'Name': 'tag:Flag', 'Values': [dcName,]},
#         ],
    )['DBInstances']

    dbiList = []
    for db in dbis:
        dbiItem = {
            'dbiId': db['DBInstanceIdentifier'],
            'rdsRole': 'Instance',
            'dbiEngine': db['Engine'],
            'engineVer': db['EngineVersion'],
            'dbiStatus': 'available',
            'dbiSize': db['DBInstanceClass'],
            'vcpuNum': 1,
            'ramSize': 2,
            'volumeSize': 20,
            'dbiAz': db['AvailabilityZone'],
            'multiAz': db['MultiAZ'],
#             'dbiEndpoint': db['Endpoint'].get('Address'),
            'createTime': db['InstanceCreateTime'].isoformat()
        }
        
        flagTag = next((tag['Value'] for tag in db['TagList'] if tag["Key"] == 'Flag'), None)
        if flagTag == dcName:
                dbiList.append(dbiItem)
    return dbiList

# 在lambda_handle() 调用以上方法   
def lambda_handler(event, context):
    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table('easyun-inventory-database')    
    dcList = get_dc_list()

    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = This_Region )

    for dc in dcList:
        invtList = list_dbinstances(dc)
        newItem={
            'dcName': dc,
            'dcInventory': invtList
        }
        table.put_item(Item = newItem)    

    return {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }
