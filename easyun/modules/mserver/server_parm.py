# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get Server Parameters, like: AMI id,instance type
@LastEditors: 
'''
from warnings import filters
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.result import Result
from datetime import date, datetime
from . import bp, REGION
from flask import jsonify


'''预定义支持的OS列表'''
AMI_Win = [
    'Windows_Server-2012-R2_RTM-English-64Bit-Base-2021.11.10',
    'Windows_Server-2016-English-Full-Base-2021.11.10',
    'Windows_Server-2019-English-Full-Base-2021.11.10',
    'Windows_Server-2022-English-Full-Base-2021.11.16'
]
AMI_Lnx = [
    'amzn2-ami-kernel-5.10-hvm-2.0.20211201.0-x86_64-gp2',
    'RHEL-8.4.0_HVM-20210504-x86_64-2-Hourly2-GP2',
    'suse-sles-15-sp2-v20201211-hvm-ssd-x86_64',
    'suse-sles-12-sp5-v20201212-hvm-ssd-x86_64',
    'ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20211021',
    'ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20211027',
    'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20210928',
    'debian-10-amd64-20210208-542'
]

class ImagesIn(Schema):
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #The image architecture ( x86_64 | arm64 )
        example="x86_64"
    )
    platform = String(
        required=True, 
        validate=OneOf(['windows', 'linux']),  #The OS platform ( Windows | Linux )
        example="linux"
    )


# @bp.get('/<arch>/<platform>')
@bp.post('/ls_images')
@auth_required(auth_token)
@input(ImagesIn)
# @output()
def list_Images(ImagesIn):
    '''获取当前环境下可用的AMIs列表'''    
    if ImagesIn['platform'] == 'windows':
        filters = [
            {'Name': 'state','Values': ['available']},
            {'Name': 'image-type','Values': ['machine']},
            {'Name': 'platform','Values': ['windows']}, # for Windows only
            {'Name': 'virtualization-type', 'Values': ['hvm']},
            {'Name': 'architecture','Values': [ImagesIn['arch']]},
            {'Name': 'name','Values': AMI_Win},
        ]
    else:
        filters = [
            {'Name': 'state','Values': ['available']},
            {'Name': 'image-type','Values': ['machine']},
            {'Name': 'virtualization-type', 'Values': ['hvm']},
            {'Name': 'architecture','Values': [ImagesIn['arch']]},
            {'Name': 'name','Values': AMI_Lnx},
        ]

    try:
        client_ec2 = boto3.client('ec2', region_name=REGION)
        images = client_ec2.describe_images(
    #         Owners=['amazon'],
            Filters = filters        
        )
        ids = [image['ImageId'] for image in images['Images']]        
        ec2 = boto3.resource('ec2', region_name=REGION)
        resp = [] 
        for id in ids:
            ami = ec2.Image(id)
            image = {
                'ami_id':id, 
                'name':ami.name,
                'platform_details':ami.platform_details,
                'description':ami.description,
                'root_device_name':ami.root_device_name,
                'root_device_type':ami.root_device_type
            }
            resp.append(image) 

        response = Result(
        detail = resp,
        # detail=[{
        #         'ami_id':id, 
        #         'name':ec2.Image(id).name,
        #         'platform':ec2.Image(id).platform,
        #         'platform_details':ec2.Image(id).platform_details,
        #         'description':ec2.Image(id).description,
        #         'root_device_name':ec2.Image(id).root_device_name,
        #         'root_device_type':ec2.Image(id).root_device_type
        #         } for id in ids
        #         ],
        status_code=3001
        )
        return response.make_resp()
            
    except Exception as ex:
        response = Result(
            message= ex, status_code=3001,http_status_code=400
        )
        response.err_resp()



Instance_Family = [
    'all',          #所有实例类型
    't2', 't3', 't3a', 'm4', 'm5', 'm5a', 'm6', 'm6a', 't4g', 'm6g', 'a1',          #通用计算 
    'c4', 'c5', 'c5a', 'c6i', 'c6g', 'c7g',         #计算优化
    'r4', 'r5', 'r5a', 'r5b', 'r5n', 'r5dn', 'r6i', 'x1', 'z1d', 'x2idn', 'x2iedn', 'x2iezn', 'R6g','X2g',          #内存优化型
    'p2', 'p3', 'p4', 'dl1', 'inf1', 'g3', 'g4dn', 'g4ad', 'g5', 'g5g', 'f1', 'vt1',            #加速计算型
    'd2', 'd3', 'd3en', 'i3', 'i3en', 'i4i', 'Is4gen', 'Im4gn', 'h1'                #内存优化型 
]

class InstypesIn(Schema):
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #The CPU architecture ( x86_64 | arm64 )
        example="x86_64"
    )
    family = String( 
        required=True, 
        validate=OneOf(Instance_Family),
        example="all"
    )

@bp.post('/ls_instypes')
@auth_required(auth_token)
@input(InstypesIn)
def list_ins_types(InstypesIn):
    '''获取当前环境下可用的Instance Types列表'''    
    family = InstypesIn['family']
    arch = InstypesIn['arch']
    if family == 'all':
        filters=[
#             {'Name': 'hypervisor', 'Values': ['nitro']},
#             {'Name': 'free-tier-eligible', 'Values': ['true']}, 
            {'Name': 'processor-info.supported-architecture', 'Values': [arch]}, 
            {'Name': 'current-generation', 'Values': ['true']},
            ]
    else:
        family = family +"."+"*"
        filters=[ 
            {'Name': 'processor-info.supported-architecture', 'Values': [arch]}, 
            {'Name': 'current-generation', 'Values': ['true']},
            {'Name': 'instance-type', 'Values': [family+'*']}
            ]
    
    try:
        client_ec2 = boto3.client('ec2', region_name = REGION)
        # instypes = client_ec2.describe_instance_types(
        #     #InstanceTypes=['t2.micro']
        #     Filters = filters,
        # )  
        describe_args = {}
        ec2_types = []
        while True:
            describe_result = client_ec2.describe_instance_types(
                **describe_args,
                Filters = filters,
            )
    #         print(describe_result.keys())
            for i in describe_result['InstanceTypes']:
                tmp = {
                    "InstanceType": i['InstanceType'],
                    "VCpu": i['VCpuInfo']['DefaultVCpus'],
                    # "VCpu": "{} vCPU".format(i['VCpuInfo']['DefaultVCpus']),
                    "Memory": i['MemoryInfo']['SizeInMiB']/1024,
                    # "Memory": "{} GiB".format(i['MemoryInfo']['SizeInMiB']/1024),
                    "Network": i['NetworkInfo']['NetworkPerformance'],
                    "Price": "",
                }
                ec2_types.append(tmp)
            if 'NextToken' not in describe_result:
                break
            describe_args['NextToken'] = describe_result['NextToken']
        # return instypes
        # print(ec2_types)
        response = Result(
            detail = ec2_types,
            status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=3001,http_status_code=400
        )
        response.err_resp()