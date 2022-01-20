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
    PublicIpAddress = String()


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
    ServerState = String()
    Tenancy = String()
    TerminalProtection = String()
    BlockDeviceMappings = List(Dict())
    NetworkInterfaces = List(Dict())
    SecurityGroups = List(Dict())
    


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
        ec2 = boto3.resource('ec2')
        instance_res1 = ec2.Instance(instance_res['InstanceId'])

        instance_type = CLIENT.describe_instance_types(InstanceTypes=[instance_res['InstanceType']])
        VCpu = instance_type['InstanceTypes'][0]["VCpuInfo"]["DefaultVCpus"]
        Memory = instance_type['InstanceTypes'][0]["MemoryInfo"]["SizeInMiB"]/1024

        images = CLIENT.describe_images(ImageIds=[instance_res['ImageId']])
        protection = CLIENT.describe_instance_attribute(InstanceId = instance_res['InstanceId'],Attribute = 'disableApiTermination')['DisableApiTermination']['Value']
        # print(images["Images"][0]["ImageLocation"])
        # print(images["Images"][0]["Name"])
        # print(instance_type)
        # print(instance_res)
        
        instance_res['Monitoring'] = instance_res['Monitoring']['State']
        instance_res['VCpu'] = VCpu
        instance_res['Memory'] = Memory
        instance_res['IamInstanceProfile'] = instance_res['IamInstanceProfile']['Arn'].split('/')[-1]
        instance_res['ImageName'] = images["Images"][0]["Name"].split('/')[-1]
        # instance_res['ImagePath'] = images["Images"][0]["ImageLocation"]
        instance_res['ImagePath'] = '/'.join(images["Images"][0]["ImageLocation"].split('/')[1:])
        instance_res['ServerState'] = instance_res['State']['Name']
        instance_res['PublicIpAddress'] = instance_res1.public_ip_address
        instance_res['Tenancy'] = 'default'
        instance_res['TerminalProtection'] = 'disabled' if protection else 'enabled'

        res = Result(detail = instance_res, status_code=200)
        return res.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()  