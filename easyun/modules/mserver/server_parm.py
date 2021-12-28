# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get Server Parameters, like: AMI id,instance type
@LastEditors: aleck
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result
from . import bp
from .ec2_attrs import AMI_Win, AMI_Lnx, Instance_Types, Instance_OS
import ast, random


class ImagesIn(Schema):
    # datacenter basic parm
    dcRegion = String(required=True, example="us-east-1")
    # parameters for image
    imgArch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #The image architecture ( x86_64 | arm64 )
        example="x86_64"
    )
    imgPlatform = String(
        required=True, 
        validate=OneOf(['windows', 'linux']),  #The OS platform ( Windows | Linux )
        example="linux"
    )

# @bp.get('/<arch>/<platform>')
@bp.post('/ls_images')
@auth_required(auth_token)
@input(ImagesIn)
# @output()
def list_images(parm):
    '''获取可用的AMI列表和系统盘信息'''
    if parm['imgPlatform'] == 'windows':
        ami_list = AMI_Win
        def split_name(imgName):
            pass

    elif parm['imgPlatform'] == 'linux':
        ami_list = AMI_Lnx
        def split_name(imgName):
            pass

    filters = [
        {'Name': 'state','Values': ['available']},
        {'Name': 'image-type','Values': ['machine']},
        # {'Name': 'platform','Values': ['windows']}, # for Windows only        
        {'Name': 'virtualization-type', 'Values': ['hvm']},
        {'Name': 'architecture','Values': [parm['imgArch']]},
        {'Name': 'name','Values': [ami['amiName'] for ami in ami_list]},
    ]

    try:
        client_ec2 = boto3.client('ec2', region_name=parm['dcRegion'])
        result = client_ec2.describe_images(
    #         Owners=['amazon'],
            Filters = filters
        )

        resp = Result(
            detail=[
                {
                    # image properties
                    'imgID': img['ImageId'],
                    'imgName': [ami['imgName'] for ami in ami_list if ami['amiName']==img['Name']][0],
                    'imgVersion' : [ami['imgVersion'] for ami in ami_list if ami['amiName']==img['Name']][0],
                    'imgCode': [ami['imgCode'] for ami in ami_list if ami['amiName']==img['Name']][0],
                    'imgDescription': img['Description'],
                    # disk parameters        
                    'root_device_name': img['RootDeviceName'],
                    'root_device_type': img['RootDeviceType'],
                    'root_device_disk': img['BlockDeviceMappings'][0]['Ebs']
                } for img in result['Images']
            ],
            status_code=200
        )
        return resp.make_resp()
            
    except Exception as ex:
        response = Result(
            message= ex, status_code=3010
        )
        response.make_resp()


# 定义 insFamily 有效取值范围
Instance_Family = ['all']
for i in Instance_Types:
    Instance_Family.extend(i['insFamily'])

class InstypesIn(Schema):
    # datacenter basic parm
    dcRegion = String(required=True, example="us-east-1")

    insArch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #The CPU architecture ( x86_64 | arm64 )
        example="x86_64"
    )
    insFamily = String( 
        required=True, 
        validate=OneOf(Instance_Family),
        example="c4"
    )
    imgCode = String(
        required=False, 
        example="linux"        
    )

@bp.post('/ls_instypes')
@auth_required(auth_token)
@input(InstypesIn)
def list_ins_types(parm):
    '''获取可用的Instance Types及价格列表'''    
    family = parm['insFamily']
    arch = parm['insArch']
    imgCode = parm['imgCode']
    # 跟进 Image code 匹配 OS
    if imgCode in ['amzn2', 'ubuntu', 'debian', 'linux']:
        insOS = 'Linux'
    elif imgCode == 'rhel':
        insOS = 'RHEL'
    elif imgCode == 'sles':
        insOS = 'SUSE' 
    elif imgCode == 'windows':
        insOS = 'Windows'
    else: 
        insOS = 'NA'    


    if family == 'all':
        filters=[
#             {'Name': 'hypervisor', 'Values': ['nitro']},
#             {'Name': 'free-tier-eligible', 'Values': ['true']}, 
            {'Name': 'processor-info.supported-architecture', 'Values': [arch]}, 
            {'Name': 'current-generation', 'Values': ['true']},
            ]
    else:
        family = family+"."+"*"
        filters=[ 
            {'Name': 'processor-info.supported-architecture', 'Values': [arch]}, 
            {'Name': 'current-generation', 'Values': ['true']},
            {'Name': 'instance-type', 'Values': [family+'*']}
            ]
    
    try:
        client_ec2 = boto3.client('ec2', region_name=parm['dcRegion'])
        # instypes = client_ec2.describe_instance_types(
        #     #InstanceTypes=['t2.micro']
        #     Filters = filters,
        # )  
        describe_args = {}
        ins_types = []
        while True:
            result = client_ec2.describe_instance_types(
                **describe_args,
                Filters = filters,
            )
    #         print(describe_result.keys())
            for i in result['InstanceTypes']:
                tmp = {
                    "InstanceType": i['InstanceType'],
                    "VCpu": i['VCpuInfo']['DefaultVCpus'],
                    # "VCpu": "{} vCPU".format(i['VCpuInfo']['DefaultVCpus']),
                    "Memory": i['MemoryInfo']['SizeInMiB']/1024,
                    # "Memory": "{} GiB".format(i['MemoryInfo']['SizeInMiB']/1024),
                    "Network": i['NetworkInfo']['NetworkPerformance'],                    
                    "Price": ec2_monthly_cost(parm['dcRegion'],i['InstanceType'], insOS),
                }
                ins_types.append(tmp)
            if 'NextToken' not in result:
                break
            describe_args['NextToken'] = result['NextToken']
        # return instypes
        # print(ec2_types)
        response = Result(
            detail = ins_types,
            status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=3020
        )
        return response.make_resp()

# 获取实例价格功能实现
def ec2_pricelist(region, instype, os, soft='NA', option='OnDemand',tenancy='Shared'):
    '''获取EC2的价格列表(单位时间Hrs)'''
    client_price = boto3.client('pricing')
    try:
        result = client_price.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'ServiceCode','Value': 'AmazonEC2'},
                {'Type': 'TERM_MATCH', 'Field': 'locationType','Value': 'AWS Region'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus','Value': 'UnusedCapacityReservation'},             
                {'Type': 'TERM_MATCH', 'Field': 'RegionCode','Value': region},
                {'Type': 'TERM_MATCH', 'Field': 'marketoption','Value': option},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy','Value': tenancy},
                {'Type': 'TERM_MATCH', 'Field': 'instanceType','Value': instype},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem','Value': os},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw','Value': soft},
            ],
        )
        prod = ast.literal_eval(result['PriceList'][0])
        price1 = prod['terms'][option]  
        key1 = list(price1.keys())[0]
        price2 = price1[key1]['priceDimensions']
        key2 = list(price2.keys())[0]
        price3 = price2[key2]
        return price3
    except Exception as ex:
        return ex

def ec2_monthly_cost(region, instype, os):
    if os == 'NA':
        return None
    try:
        pricelist = ec2_pricelist(region, instype, os)
        unit = pricelist.get('unit')
        currency = list(pricelist['pricePerUnit'].keys())[0]
        unitePrice = pricelist['pricePerUnit'].get(currency)
        if unit == 'Hrs':
            monthPrice = float(unitePrice)*730
        return {
            'value': monthPrice,
            'currency' : currency
        }

    except Exception as ex:
        return ex
