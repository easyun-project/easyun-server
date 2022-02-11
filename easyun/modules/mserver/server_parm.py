# -*- coding: utf-8 -*-
"""
  @module:  Server Management - parameters
  @desc:    Get parameters to create new server, like: AMI id,instance type
  @auth:    
"""

import boto3
import ast, random, json
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict, Nested
from apiflask.validators import Length, OneOf
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.cloud.aws_ec2_ami import AMI_Win, AMI_Lnx
from easyun.cloud.aws_ec2_instype import Instance_Family, get_familyDes


class ImageQuery(Schema):
    # query parameters for instance image 
    dc = String(
        required=True, 
        validate=Length(0, 30),
        example='Easyun'
    )    
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #Image architecture ( x86_64 | arm64 )
        example="x86_64"
    )
    os = String(
        required=True, 
        validate=OneOf(['windows', 'linux']),  #OS platform ( Windows | Linux )
        example="linux"
    )

@bp.get('/param/image')
@auth_required(auth_token)
@input(ImageQuery, location='query')
# @output()
def list_images( parm):
    '''获取可用的AMI列表(包含 System Disk信息)'''

    imgArch = parm.get('arch')
    # if imgArch not in ['x86_64', 'arm64']:
    #     resp = Result(
    #         detail='Unknown image architecture. The valure must be one of: x86_64, arm64.',
    #         message='Validation error',
    #         status_code=3011,
    #         http_status_code=400
    #     )
    #     return resp.err_resp()
    imgOS = parm.get('os')        
    if imgOS == 'windows':
        amiList = AMI_Win.get(str(imgArch)) 
        # 从image name中截取有意义字段
        def split_name(imgName):
            pass
    elif imgOS == 'linux':
        amiList = AMI_Lnx.get(str(imgArch)) 
        def split_name(imgName):
            pass
    else:
        resp = Result(
            detail='Unknown image architecture. The valure must be one of: windows, linux.',
            message='Validation error',
            status_code=3011,
            http_status_code=400
        )
        return resp.err_resp()

    filters = [
        {'Name': 'state','Values': ['available']},
        {'Name': 'image-type','Values': ['machine']},
        # {'Name': 'platform','Values': ['windows']}, # for Windows only        
        {'Name': 'virtualization-type', 'Values': ['hvm']},
        {'Name': 'architecture','Values': [imgArch]},
        {'Name': 'name','Values': [ami.get('amiName') for ami in amiList]},
    ]

    try:
        thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
        dcRegion = thisDC.get_region()

        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name = dcRegion )  

        client_ec2 = boto3.client('ec2')
        result = client_ec2.describe_images(
    #         Owners=['amazon'],
            Filters = filters
        )

        imgList = [
            {
                # image properties
                'imgID': img['ImageId'],
                'osName': [ami['osName'] for ami in amiList if ami['amiName']==img['Name']][0],
                'osVersion' : [ami['osVersion'] for ami in amiList if ami['amiName']==img['Name']][0],
                'osCode': [ami['osCode'] for ami in amiList if ami['amiName']==img['Name']][0],
                'imgDescription': img['Description'],
                # root disk parameters
                'rootDevice' : {
                    'devicePath': img['RootDeviceName'],
                    'deviceType': img['RootDeviceType'],
                    'deviceDisk': img['BlockDeviceMappings'][0].get('Ebs')                    
                }
            } for img in result['Images']
        ]
        resp = Result(
            detail=imgList,
            message = "success,"+ str(len(imgList)),
            status_code=200
        )
        return resp.make_resp()
            
    except Exception as ex:
        response = Result(
            message= ex, status_code=3010
        )
        return response.make_resp()



class InsFamilyQuery(Schema):
    # query parameters for instance family 
    dc = String(
        required=True, 
        validate=Length(0, 60),      
        example='Easyun'
    )
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #Processor architecture ( x86_64 | arm64 )
        example="x86_64"
    )

@bp.get('/param/insfamily')
@auth_required(auth_token)
@input(InsFamilyQuery, location='query')
def get_ins_family(parm):
    '''获取可用的Instance Family列表'''
    insArch = parm.get('arch')
    # if insArch not in ['x86_64', 'arm64']:
    #     resp = Result(
    #         detail='Unknown image architecture. The valure must be one of: x86_64, arm64.',
    #         message='Validation error',
    #         status_code=3012,
    #         http_status_code=400
    #     )
    #     return resp.err_resp()
    #         
    filters=[
        {'Name': 'processor-info.supported-architecture', 'Values': [insArch]}, 
        {'Name': 'current-generation', 'Values': ['true']},
    ]
    try:
        # this_dc = Datacenter(name=dcname)
        thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
        dcRegion = thisDC.get_region()
        client_ec2 = boto3.client('ec2', region_name = dcRegion)
        # 基于NextToken判断获取完整 instance types 列表
        desc_args = {}
        instypeList = []
        while True:
            result = client_ec2.describe_instance_types(
                **desc_args,
                Filters = filters,
            )
    #         print(describe_result.keys())
            for i in result['InstanceTypes']:
                insType = i['InstanceType']
                insFamily = insType.split('.')[0]
                tmp = {
                    'insType': insType,
                    'insFamily': insFamily,
                    'familyDes': get_familyDes(insFamily)
                }
                instypeList.append(tmp)
            if 'NextToken' not in result:
                break
            desc_args['NextToken'] = result['NextToken']
        # return instypes
        # print(ec2_types)
        response = Result(
            detail = instypeList,
            message = "success,"+ str(len(instypeList)),
            status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=3020
        )
        return response.err_resp()



# 定义 insFamily 有效取值范围
InsFamily_All = ['all']
for i in Instance_Family:
    familyList = [f['familyName'] for f in i['insFamily']]
    InsFamily_All.extend(familyList)

class InsTypeQuery(Schema):
    # query parameters for instance type 
    dc = String(
        required=True, 
        validate=Length(0, 60),      
        example='Easyun'
    )
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #Processor architecture ( x86_64 | arm64 )
        example="x86_64"
    )
    family = String( 
        required=True, 
        validate=OneOf(InsFamily_All),
        example="m5"
    )
    os = String(
        required=False, 
        validate=OneOf(['amzn2', 'ubuntu', 'debian', 'linux','rhel','sles','windows']),         
        example="linux"        
    )

@bp.get('/param/instype')
@auth_required(auth_token)
@input(InsTypeQuery, location='query')
def list_ins_types(parm):
    '''获取可用的Instance Types列表(含月度成本)'''
    insArch = parm['arch']
    insFamily = parm['family']
    if insFamily == 'all':
        filters=[
#             {'Name': 'hypervisor', 'Values': ['nitro']},
#             {'Name': 'free-tier-eligible', 'Values': ['true']}, 
            {'Name': 'processor-info.supported-architecture', 'Values': [insArch]}, 
            {'Name': 'current-generation', 'Values': ['true']},
            ]
    else:
        insFamily = insFamily+"."+"*"
        filters=[ 
            {'Name': 'processor-info.supported-architecture', 'Values': [insArch]}, 
            {'Name': 'current-generation', 'Values': ['true']},
            {'Name': 'instance-type', 'Values': [insFamily]}
            ]
    
    try:
        thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
        dcRegion = thisDC.get_region()
        client_ec2 = boto3.client('ec2', region_name = dcRegion)
        # 基于NextToken判断获取完整 instance types 列表
        describe_args = {}
        instypeList = []
        while True:
            result = client_ec2.describe_instance_types(
                **describe_args,
                Filters = filters,
            )
    #         print(describe_result.keys())
            for i in result['InstanceTypes']:
                tmp = {
                    "insType": i['InstanceType'],
                    "vcpuNum": i['VCpuInfo']['DefaultVCpus'],
                    # "VCpu": "{} vCPU".format(i['VCpuInfo']['DefaultVCpus']),
                    "memSize": i['MemoryInfo']['SizeInMiB']/1024,
                    # "Memory": "{} GiB".format(i['MemoryInfo']['SizeInMiB']/1024),
                    "netSpeed": i['NetworkInfo']['NetworkPerformance'],                    
                    "monthPrice": ec2_monthly_cost(dcRegion,i['InstanceType'], parm.get('os')),
                }
                instypeList.append(tmp)
            if 'NextToken' not in result:
                break
            describe_args['NextToken'] = result['NextToken']
        # return instypes
        # print(ec2_types)
        response = Result(
            detail = instypeList,
            message = "success,"+ str(len(instypeList)),
            status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=3020
        )
        return response.make_resp()


def ec2_monthly_cost(region, instype, os):
    '''获取EC2的月度成本(单位时间Month)'''
    if not os:
        return None
    try:
        pricelist = ec2_pricelist(region, instype, os)
        unit = pricelist.get('unit')
        currency = list(pricelist['pricePerUnit'].keys())[0]
        unitePrice = pricelist['pricePerUnit'].get(currency)
        if unit == 'Hrs':
            # 参考AWS做法按每月730h计算
            monthPrice = float(unitePrice)*730
        return {
            'value': monthPrice,
            'currency' : currency
        }
    except Exception as ex:
        return ex

# 获取实例价格功能实现部分
def ec2_pricelist(
        region, instype, os, 
        soft='NA', 
        option='OnDemand',
        tenancy='Shared'
    ):
    '''获取EC2的价格列表(单位时间Hrs)'''
    # AWS Price API only support us-east-1, ap-south-1
    priceRegion = 'us-east-1'

    # 将传入的 os 匹配为 price api 支持的 operatingSystem
    if os in ['amzn2', 'ubuntu', 'debian', 'linux']:
        insOS = 'Linux'
    elif os == 'rhel':
        insOS = 'RHEL'
    elif os == 'sles':
        insOS = 'SUSE' 
    elif os == 'windows':
        insOS = 'Windows'
    else: 
        insOS = 'NA'

    try:
        client_price = boto3.client('pricing', region_name= priceRegion )
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
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem','Value': insOS},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw','Value': soft},
            ],
        )
        # 通过 ast.literal_eval()函数 对字符串进行类型转换
        prod = ast.literal_eval(result['PriceList'][0])
        price1 = prod['terms'].get(option)  
        key1 = list(price1.keys())[0]
        price2 = price1[key1]['priceDimensions']
        key2 = list(price2.keys())[0]
        price3 = price2[key2]
        return price3
    except Exception as ex:
        return ex
