"""
  @module:  Dashboard lambda function
  @desc:    抓取所有数据中心的对象存储(S3)数据并写入ddb
  @auth:    xdq
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
    resource_ddb = boto3.resource('dynamodb', region_name=deploy_region)
    table = resource_ddb.Table(Inventory_Table)
    dcList = table.get_item(
        Key={'dc_name': 'all', 'invt_type': 'dclist'}
    )['Item'].get('invt_list')
    return dcList


def get_bucket_access(s3_client, name):
    try:
        # 获取存储桶的权限
        access = s3_client.get_public_access_block(Bucket=name)
        if access['PublicAccessBlockConfiguration']['BlockPublicPolicy'] == False or \
                access['PublicAccessBlockConfiguration']['IgnorePublicAcls'] == False or \
                access['PublicAccessBlockConfiguration']['BlockPublicPolicy'] == False or \
                access['PublicAccessBlockConfiguration']['BlockPublicPolicy'] == False:
            bucketStatus = 'Objects can be public'
        else:
            bucketStatus = 'Bucket and objects not public'
    except Exception as e:
        if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
            # print('\t no Public Access')
            bucketStatus = 'Objects can be public'
        else:
            print("unexpected error: %s" % (e.response))
    return bucketStatus


def get_bucket_encryption(s3_client, name):
    try:
        resp = s3_client.get_bucket_encryption(Bucket=name)
        encryption = resp['ServerSideEncryptionConfiguration']['Rules'][0]['BucketKeyEnabled']
    except Exception as e:
        if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
            encryption = False
        else:
            print("unexpected error: %s" % (e.response))
    return encryption


def list_buckets(dcName):
    s3_client = boto3.client('s3', region_name=this_region)
    s3_resource = boto3.resource('s3')
    bucket_list = []
    for b in s3_resource.buckets.filter(
            Filters=[
                {'Name': 'tag:Flag', 'Values': [dcName]}
            ]
    ):
        bucket_versioning = s3_resource.BucketVersioning(b.name)
        bucket = {
            'bucketIdentifier': b.name,
            'bucketRegion': s3_client.get_bucket_location(Bucket=b.name).get("LocationConstraint") or 'us-east-1',
            'bucketAccess': get_bucket_access(s3_client, b.name),
            'bucketEncryption': get_bucket_encryption(s3_client, b.name),
            'bucketVersiong': bucket_versioning.status,
            'createTime': b.creation_date.isoformat()
        }
        bucket_list.append(bucket)
    return bucket_list


# 在lambda_handle() 调用以上方法
def lambda_handler(event, context):
    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = Deploy_Region)

    resource_ddb = boto3.resource('dynamodb')
    table = resource_ddb.Table("easyun-inventory-stobject")
    dcList = get_dc_list()
    for dc in dcList:
        invtList = list_buckets(dc)
        newItem={
            'dcName': dc,
            'dcInventory': invtList
        }
        table.put_item(Item = newItem)    

    return {
        'statusCode': 200,
        'body': json.dumps('loaded!')
    }
