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
from easyun.common.models import Datacenter
from easyun.common.result import Result
from . import bp
from .ec2_attrs import AMI_Win, AMI_Lnx, Instance_Family, get_familyDes, Instance_OS
import ast, random, json


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
@bp.post('/images')
@auth_required(auth_token)
@input(ImagesIn)
# @output()
def list_images(parm):
    '''获取可用的AMI列表(包含 System Disk信息)'''
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

        imgList = [
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




@bp.get('/<dcname>/<arch>/insfamily')
@auth_required(auth_token)
def get_ins_family(dcname,arch):
    '''获取可用的Instance Family列表'''
    filters=[
        {'Name': 'processor-info.supported-architecture', 'Values': [arch]}, 
        {'Name': 'current-generation', 'Values': ['true']},
    ]    
    try:
        # this_dc = Datacenter(name=dcname)
        this_dc = Datacenter.query.filter_by(name=dcname).first()
        dcRegion = this_dc.get_region()
        client_ec2 = boto3.client('ec2', region_name=dcRegion)
        # instypes = client_ec2.describe_instance_types(
        #     #InstanceTypes=['t2.micro']
        #     Filters = filters,
        # )  
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
        validate=OneOf(InsFamily_All),
        example="c4"
    )
    imgCode = String(
        required=False, 
        example="linux"        
    )

@bp.post('/instypes')
@auth_required(auth_token)
@input(InstypesIn)
def list_ins_types(parm):
    '''获取可用的Instance Types列表(含月度成本)'''    
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
        instypeList = []
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

# 获取实例价格功能实现部分
def ec2_pricelist(region, instype, os, soft='NA', option='OnDemand',tenancy='Shared'):
    '''获取EC2的价格列表(单位时间Hrs)'''
    # AWS Price API only support us-east-1, ap-south-1
    priceRegion = 'us-east-1'
    client_price = boto3.client('pricing', region_name= priceRegion )
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

def ec2_monthly_cost(region, instype, os):
    '''获取EC2的月度成本(单位时间Month)'''
    if os == 'NA':
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
