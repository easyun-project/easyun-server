"""
  @module:  Easyun Deployment - DynamoDB
  @desc:    Create dynamodb for inventory data
  @auth:    aleck
"""
import boto3


Deploy_Region = 'us-east-1'


def ddb_creator(tabName):
    resource_ddb = boto3.resource('dynamodb', region_name= Deploy_Region)
    table = resource_ddb.create_table(
        TableName = tabName,
        KeySchema=[
            {
                'AttributeName': 'dc_name',
                'KeyType': 'HASH' # Partition key
            },
            {
                'AttributeName': 'invt_type',
                'KeyType': 'RANGE'  # Sort key
            }         
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'dc_name',
                'AttributeType': 'S'  #字符串
            },
            {
                'AttributeName': 'invt_type',
                'AttributeType': 'S'  #字符串
            }, 
#             {
#                 'AttributeName': 'invt_list',
#                 'AttributeType': 'S'
#             }, 
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    # 等待ddb table创建完成
    table.meta.client.get_waiter('table_exists').wait(TableName=tabName)
    return table.name