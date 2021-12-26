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
from .models import AMI_Win, AMI_Lnx
import random


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
        images = result['Images']

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
                } for img in images
            ],
            status_code=200
        )
        return resp.make_resp()
            
    except Exception as ex:
        response = Result(
            message= ex, status_code=3010
        )
        response.make_resp()


# 此处有待优化处理
Instance_Family = [
    'all',          #所有实例类型
    't2', 't3', 't3a', 'm4', 'm5', 'm5a', 'm6', 'm6a', 't4g', 'm6g', 'a1',          #通用计算 
    'c4', 'c5', 'c5a', 'c6i', 'c6g', 'c7g',         #计算优化
    'r4', 'r5', 'r5a', 'r5b', 'r5n', 'r5dn', 'r6i', 'x1', 'z1d', 'x2idn', 'x2iedn', 'x2iezn', 'R6g','X2g',          #内存优化型
    'p2', 'p3', 'p4', 'dl1', 'inf1', 'g3', 'g4dn', 'g4ad', 'g5', 'g5g', 'f1', 'vt1',            #加速计算型
    'd2', 'd3', 'd3en', 'i3', 'i3en', 'i4i', 'Is4gen', 'Im4gn', 'h1'                #内存优化型 
]

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
        example="all"
    )

@bp.post('/ls_instypes')
@auth_required(auth_token)
@input(InstypesIn)
def list_ins_types(parm):
    '''获取可用的Instance Types列表'''    
    family = parm['insFamily']
    arch = parm['insArch']
    # 获取价格部分功能待实现
    # 返回随机数便于前端测试排序
    def list_price():
        price = random.randint(1,10)
        return price

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
                    "Price": list_price(),
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
        response.make_resp()