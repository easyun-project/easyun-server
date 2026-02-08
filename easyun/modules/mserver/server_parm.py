# -*- coding: utf-8 -*-
"""
  @module:  Server Management - parameters
  @desc:    Get parameters to create new server, like: AMI id,instance type
  @auth:    
"""
import boto3
from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Nested
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.cloud.utils import set_boto3_region
from easyun.cloud.aws_ec2_ami import AMI_Windows, AMI_Linux
from easyun.cloud.aws_price import ec2_monthly_cost
from easyun.cloud.aws_ec2_instype import Instance_Family, get_family_descode
from . import bp


class ImageQuery(Schema):
    # query parameters for instance image 
    dc = String(
        required=True, 
        validate=Length(0, 30), metadata={"example": 'Easyun'}
    )    
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #Image architecture ( x86_64 | arm64 )
        metadata={"example": "x86_64"}
    )
    os = String(
        required=True, 
        validate=OneOf(['windows', 'linux']),  #OS platform ( Windows | Linux )
        metadata={"example": "linux"}
    )

@bp.get('/param/image')
@bp.auth_required(auth_token)
@bp.input(ImageQuery, location='query')
# @output()
def list_images( parms ):
    '''获取可用的AMI列表(包含 System Disk信息)'''
    dcName = parms['dc']
    imgArch = parms['arch']
    imgOS = parms['os']
    amiList = AMI_Windows[str(imgArch)] if imgOS == 'windows' else AMI_Linux[str(imgArch)]

    filters = [
        {'Name': 'state','Values': ['available']},
        {'Name': 'image-type','Values': ['machine']},
        # {'Name': 'platform','Values': ['windows']}, # for Windows only
        {'Name': 'virtualization-type', 'Values': ['hvm']},
        {'Name': 'architecture','Values': [imgArch]},
        {'Name': 'name','Values': [ami.get('amiName') for ami in amiList]},
    ]

    try:
        # 设置 boto3 接口默认 region_name
        dcRegion = set_boto3_region( dcName )
        client_ec2 = boto3.client('ec2')

        # No paginator needed for describe_images
        images = client_ec2.describe_images(
    #         Owners=['amazon'],
            Filters = filters
        )['Images']

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
            } for img in images
        ]
                   
        resp = Result(
            detail=imgList,
            message = str(len(imgList))+",success",
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
        validate=Length(0, 60), metadata={"example": 'Easyun'}
    )
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #Processor architecture ( x86_64 | arm64 )
        metadata={"example": "x86_64"}
    )


@bp.get('/param/insfamily')
@bp.auth_required(auth_token)
@bp.input(InsFamilyQuery, location='query', arg_name='parm')
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
    try:
        familyList = []
        for familyDict in Instance_Family:
            subFamily = familyDict['familyList']
            for f in subFamily:
                if f['architecture'] == insArch:
                    tmp = {
                        'catgName': familyDict['catgName'],
                        'catdesCode': familyDict['catdesCode'],
                        'familyName': f['name'],
                        'familyDes': f['description']
                    }
                    familyList.append(tmp)

        response = Result(
            detail = familyList,
            message = str(len(familyList))+",success",
            status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, 
            status_code=3020
        )
        return response.err_resp()



# 定义 insFamily 有效取值范围
InsFamily_All = ['all']
for i in Instance_Family:
    familyList = [f['name'] for f in i['familyList']]
    InsFamily_All.extend(familyList)


class InsTypelsQuery(Schema):
    # query parameters for instance family 
    dc = String(
        required=True, 
        validate=Length(0, 60), metadata={"example": 'Easyun'}
    )
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #Processor architecture ( x86_64 | arm64 )
        metadata={"example": "x86_64"}
    )
    family = String( 
        required=True, 
        validate=OneOf(InsFamily_All), metadata={"example": "m5"}
    )


@bp.get('/param/instype/list')
@bp.auth_required(auth_token)
@bp.input(InsTypelsQuery, location='query', arg_name='parm')
def get_ins_type_list(parm):
    '''获取可用的Instance Types列表(不含成本)'''
    insArch = parm.get('arch')
    insFamily = parm['family']
    if insFamily == 'all':
        filters=[
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
        # this_dc = Datacenter(name=dcname)
        thisDC = Datacenter.query.filter_by(name = parm['dc']).first()
        dcRegion = thisDC.get_region()
        client_ec2 = boto3.client('ec2', region_name = dcRegion)
        # 基于NextToken判断获取完整 instance types 列表
        desc_args = {
            'Filters' : filters,
        }
        instypeList = []
        while True:
            result = client_ec2.describe_instance_types( **desc_args )
    #         print(describe_result.keys())
            for i in result['InstanceTypes']:
                insType = i['InstanceType']
                insFamily = insType.split('.')[0]
                tmp = {
                    'insType': insType,
                    'familyName': insFamily,
                    'familyDes': get_family_descode(insFamily)
                }
                instypeList.append(tmp)
            if 'NextToken' not in result:
                break
            desc_args['NextToken'] = result['NextToken']
        # return instypes
        # print(ec2_types)
        response = Result(
            detail = instypeList,
            message = str(len(instypeList))+",success",
            status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=3020
        )
        return response.err_resp()


class InsTypeQuery(Schema):
    # query parameters for instance type 
    dc = String(
        required=True, 
        validate=Length(0, 60), metadata={"example": 'Easyun'}
    )
    arch = String(
        required=True, 
        validate=OneOf(['x86_64', 'arm64']),  #Processor architecture ( x86_64 | arm64 )
        metadata={"example": "x86_64"}
    )
    family = String( 
        required=True, 
        validate=OneOf(InsFamily_All), metadata={"example": "m5"}
    )
    os = String(
        required=False, 
        validate=OneOf(['amzn2', 'ubuntu', 'debian', 'linux','rhel','sles','windows']), metadata={"example": "linux"}        
    )

@bp.get('/param/instype')
@bp.auth_required(auth_token)
@bp.input(InsTypeQuery, location='query', arg_name='parm')
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
            message = str(len(instypeList))+",success",
            status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        response = Result(
            message= ex, status_code=3020
        )
        return response.make_resp()
