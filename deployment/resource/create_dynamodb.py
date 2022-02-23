# -*- coding: UTF-8 -*-
"""
  @module:  Easyun Deployment - DynamoDB
  @desc:    Create dynamodb for inventory data
  @auth:    aleck
"""
import boto3
import os
import json
import argparse


CONFIG_FILE = 'deploy_config.json'
INVENTORY_TABLE = {
    'all': 'easyun-inventory-all',
    'server': 'easyun-inventory-server',
    'database': 'easyun-inventory-database',
    'st_block': 'easyun-inventory-stblock',
    'st_object': 'easyun-inventory-stobject',
    'st_file': 'easyun-inventory-stfiles',
    'nw_subnet': 'easyun-inventory-subnet',
    'nw_secgroup': 'easyun-inventory-secgroup',
    'nw_gateway': 'easyun-inventory-gateway'
}

def create_table(table_name):
    '''创建DnamoDB table'''
    # table_name = '%s-%s' % (table_name_prefix, str(uuid.uuid4()))
    resource_ddb = boto3.resource('dynamodb')
    key_schema = [
        {
            'AttributeName': 'dc_name',
            'KeyType': 'HASH',    # Partition key
        },
        {
            'AttributeName': 'invt_type',
            'KeyType': 'RANGE'    # Sort key
        }  
    ]
    attribute_definitions = [
        {
            'AttributeName': 'dc_name',
            'AttributeType': 'S'  #字符串
        },
        {
            'AttributeName': 'invt_type',
            'AttributeType': 'S'  #字符串
        }, 
            # {
            #     'AttributeName': 'invt_list',
            #     'AttributeType': 'S'
            # }, 
    ]
    # if range_key is not None:
    #     key_schema.append({'AttributeName': range_key, 'KeyType': 'RANGE'})
    #     attribute_definitions.append({'AttributeName': range_key, 'AttributeType': 'S'})
    table = resource_ddb.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5,
        }
    )
    # 等待ddb table创建完成
    waiter = table.meta.client.get_waiter('table_exists')
    waiter.wait(TableName=table_name, WaiterConfig={'Delay': 1})
    # table.meta.client.get_waiter('table_exists').wait(TableName=tabName)
    return table_name


def record_to_config(key, value, stage):
    '''将table信息记录到配置文件'''
    with open(os.path.join('.', CONFIG_FILE)) as f:
        data = json.load(f)
        data['stages'].setdefault(stage, {}).setdefault(
            'inventory_tables', {}
        )[key] = value
    with open(os.path.join('.', CONFIG_FILE), 'w') as f:
        serialized = json.dumps(data, indent=2, separators=(',', ': '))
        f.write(serialized + '\n')

def already_in_config(env_var, stage):
    '''判断table是否已经存在于配置文件'''
    with open(os.path.join('.', CONFIG_FILE)) as f:
        return env_var in json.load(f)['stages'].get(
            stage, {}).get('inventory_tables', {})

def create_resources(args):
    # 设置 boto3 接口默认 region_name
    boto3.setup_default_session(region_name = args.region)
    for invt_type in INVENTORY_TABLE.keys():
        # We assume if the value is recorded in the deploy config
        # file, the dynamodb table already exists.
        if already_in_config(invt_type, args.stage):
            continue
        table_name = INVENTORY_TABLE.get(invt_type)
        print('Creating table: ',table_name)
        table_name = create_table(table_name)
        record_to_config(invt_type, table_name, args.stage)


def cleanup_resources(args):
    client_ddb = boto3.resource('dynamodb', region_name = args.region)
    for table_name in INVENTORY_TABLE.values():
        try:
            print('Creating table: ',table_name)
            client_ddb.delete_table(TableName=table_name)
        except Exception:
            #异常忽略，暂不处理
            pass
    print("Resources deleted.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage', default='dev')
    parser.add_argument('-r', '--region', default='us-east-1')
    parser.add_argument('-c', '--cleanup', action='store_true')
    # app - stores the todo items
    # users - stores the user data.
    args = parser.parse_args()
    if args.cleanup:
        cleanup_resources(args)
    else:
        create_resources(args)


if __name__ == '__main__':
    main()
