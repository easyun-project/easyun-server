# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get info: Server list, Server detail
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from datetime import date, datetime
from . import bp, REGION
from easyun.common.result import Result, make_resp, error_resp, bad_request


class DetailOut(Schema):
    # ins_id = String()
    # tag_name = Dict()
    # ins_status = String()
    # ins_type = String()
    # vcpu = Integer()
    # ram = String()
    # subnet_id = String()
    # ssubnet_id = String()
    # key_name = String()
    # category = String()
    #缺少ipname，publicip,Terminal protection, IAM role
    InstanceType = String()
    VCpu = String()
    Memory = String()
    PrivateIpAddress = String()


    InstanceId = String()
    LaunchTime = String()

    
    PrivateDnsName = String()
    PublicDnsName = String()

    PlatformDetails = String()
    VirtualizationType = String()
    UsageOperation = String()    
    Monitoring = String()

    ImageId = String()
    ImageName = String()
    ImagePath = String()
    KeyName = String()
    IamInstanceProfile = String()
    


@bp.get('/detail/<svr_id>')
@auth_required(auth_token)
@output(DetailOut, description='Server detail info')
def get_svr(svr_id):
    '''查看指定云服务器详情'''
    CLIENT = boto3.client('ec2', region_name=REGION)

    # Helper method to serialize datetime fields
    def json_datetime_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))
    try:
        instance = CLIENT.describe_instances(InstanceIds=[svr_id])
        instance_res = [j for i in instance['Reservations'] for j in i['Instances']][0]

        instance_type = CLIENT.describe_instance_types(InstanceTypes=[instance_res['InstanceType']])
        VCpu = instance_type['InstanceTypes'][0]["VCpuInfo"]["DefaultVCpus"]
        Memory = instance_type['InstanceTypes'][0]["MemoryInfo"]["SizeInMiB"]/1024

        images = CLIENT.describe_images(ImageIds=[instance_res['ImageId']])

        # print(images["Images"][0]["ImageLocation"])
        # print(images["Images"][0]["Name"])
        # print(instance_type)
        # print(instance_res)
        
        instance_res['Monitoring'] = instance_res['Monitoring']['State']
        instance_res['VCpu'] = VCpu
        instance_res['Memory'] = Memory
        instance_res['ImageName'] = images["Images"][0]["Name"]
        instance_res['ImagePath'] = images["Images"][0]["ImageLocation"]
        res = Result(detail = instance_res, status_code=3001)
        return res.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()  


@bp.get('/instypes/<svr_id>')
# @auth_required(auth_token)
# @input()
# @output()
def get_types(svr_id):
    '''获取指定云服务器支持的Instance Types列表'''

    # 1.查询云服务器的架构 x86-64bit / arm-64bit

    # 2.查询相同架构下的Instance Types

    return ''
