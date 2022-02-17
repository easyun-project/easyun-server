# encoding: utf-8
"""
  @module:  Block Storage Module
  @desc:    块存储(EBS) Volume 卷管理相关
  @auth:    
"""

import boto3
from flask import send_file
from flask.views import MethodView
from apiflask import auth_required, Schema, input, output
from apiflask.fields import String, Integer, Boolean
from apiflask.validators import Length
from sqlalchemy import false, true
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import len_iter, query_dc_region, query_svr_name
from . import bp, TYPE
from .schemas import newVolume


# 将磁盘管理代码从服务器模块移到存储管理模块

# 定义系统盘路径
SystemDisk = ['/dev/xvda','/dev/sda1']

   
class NewDiskIn(Schema):
    InstanceId = String(required=True, example='i-0ac436622e8766a13')  #云服务器ID
    Encrypted = Boolean(required=True, example = False)
    Iops = Integer(example=3000)  
    # Iops = Integer(required=True, example=3000)
    Size = Integer(required=True, example=10)
    VolumeType = String(required=True, example='gp3')
    Throughput = Integer( example=500)
    # Throughput = Integer(required=True, example=500)
    Tag = String(required=True, example='disk_test')
    Device = String(required=True, example='/dev/sdg')


@bp.post('/volume')
@auth_required(auth_token)
@input(NewDiskIn)
# @output()
def add_disk(NewDiskIn):
    '''新增磁盘(EBS Volume)'''
    try:
        CLIENT = boto3.client('ec2')
        RESOURCE = boto3.resource('ec2')
        server =RESOURCE.Instance(NewDiskIn["InstanceId"])
        TagSpecifications = [
        {
        "ResourceType":"volume",
        "Tags": [
                {"Key": "Flag", "Value": "Easyun"},
                {"Key": "Name", "Value": NewDiskIn['Tag']}
            ]
        }
        ]
        iops = 'Iops' in NewDiskIn.keys()
        throughput = 'Throughput' in NewDiskIn.keys()
        print(iops,throughput)
        if iops and not throughput:
            volume = CLIENT.create_volume(
                AvailabilityZone = RESOURCE.Subnet(server.subnet_id).availability_zone,
                Encrypted= NewDiskIn['Encrypted'],
                Iops=NewDiskIn['Iops'],
                Size=NewDiskIn['Size'],
                VolumeType=NewDiskIn['VolumeType'],
                TagSpecifications=TagSpecifications,
            )
        elif not iops and throughput:
            volume = CLIENT.create_volume(
                AvailabilityZone = RESOURCE.Subnet(server.subnet_id).availability_zone,
                Encrypted= NewDiskIn['Encrypted'],
                Size=NewDiskIn['Size'],
                VolumeType=NewDiskIn['VolumeType'],
                TagSpecifications=TagSpecifications,
                Throughput=NewDiskIn['Throughput'],
            )
        else:
            volume = CLIENT.create_volume(
                AvailabilityZone = RESOURCE.Subnet(server.subnet_id).availability_zone,
                Encrypted= NewDiskIn['Encrypted'],
                Iops=NewDiskIn['Iops'],
                Size=NewDiskIn['Size'],
                VolumeType=NewDiskIn['VolumeType'],
                TagSpecifications=TagSpecifications,
                Throughput=NewDiskIn['Throughput'],
            )
        # print(dir(volume))
        # volume1 = RESOURCE.Volume(volume['VolumeId'])
        # waiter = CLIENT.get_waiter('volume_available')
        # waiter.wait(
        #     VolumeIds=[
        #         volume1.id,
        #     ]
        # )
        # volume1.attach_to_instance(
        #     Device=NewDiskIn["Device"],
        #     InstanceId=NewDiskIn["InstanceId"]
        # )
        from time import sleep 
        while True:
            volume1 = RESOURCE.Volume(volume['VolumeId'])
            print(volume1.state)
            if volume1.state == 'available':
                
                volume1.attach_to_instance(
                    Device=NewDiskIn["Device"],
                    InstanceId=NewDiskIn["InstanceId"]
                )
                break
            sleep(0.5)
            
        response = Result(
            detail={'VolumeId':volume1.volume_id,
            "State" : volume1.state,
            },
            status_code=200
            )
        # response = Result(
        #     detail={'VolumeId':volume['VolumeId'],
        #     "State" : volume["State"],
        #     },
        #     status_code=200
        #     )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()




@bp.post("/block/volume1")
@auth_required(auth_token)
@input(newVolume)
def post(self, data):
    '''新增磁盘(EBS Volume) 【重复】'''
    try:
        ec2Client = boto3.client('ec2')
        
        # 获取可用区信息
        az = data.get('az')
        # 创建EBS卷
        volumeEncryption = data.get('encryption')
        if volumeEncryption == 'true':
            isEncryption = True
        elif volumeEncryption == 'false':
            isEncryption = False
        
        createResult = ec2Client.create_volume(
            AvailabilityZone = az,
            Encrypted = isEncryption,
            Size = int(data.get('size')),
            VolumeType = data.get('diskType'),
            Iops = int(data.get('iops')),
            Throughput = int(data.get('thruput')),
            TagSpecifications = [{
                'ResourceType' : 'volume',
                'Tags' : [{ 'Key':'Flag','Value':'Easyun' }]
            }]
        )
        volumeId = createResult['VolumeId']
        
        response = Result(
            detail=[{
                'VolumeId' : volumeId
            }],
            status_code=5001
        )
        return response.make_resp()
    except Exception:
        response = Result(
            message='volume attach failed', status_code=5001,http_status_code=400
        )
        return response.err_resp()



class DeleteDiskIn(Schema):
    svrId = String(required=True, example='i-0ac436622e8766a13')  #云服务器ID
    diskPath = String(required=True, example='/dev/sdg')


@bp.delete('/volume')
@auth_required(auth_token)
@input(DeleteDiskIn)
# @output()
def delete_disk(DeleteDiskIn):
    '''删除磁盘(EBS Volume)'''
    try:
        CLIENT = boto3.client('ec2')
        RESOURCE = boto3.resource('ec2')
        server =RESOURCE.Instance(DeleteDiskIn["InstanceId"])
        disks = CLIENT.describe_instances(InstanceIds=[DeleteDiskIn["InstanceId"]])['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
        vid = [i['Ebs']['VolumeId'] for i in disks if i['DeviceName'] == DeleteDiskIn["Device"]]
        print(vid)
        # print(dir(volume))
        if len(vid)==0:
            raise ValueError('invalid device')
        volume = RESOURCE.Volume(vid[0])

        volume.detach_from_instance(
            Device=DeleteDiskIn["Device"],
            InstanceId=DeleteDiskIn["InstanceId"]
        )
        # waiter = CLIENT.get_waiter('volume_available')
        # waiter.wait(
        #     VolumeIds=[
        #         volume.id,
        #     ]
        # )
        from time import sleep 
        while True:
            volume1 = RESOURCE.Volume(volume.volume_id)
            print(volume1.state)
            if volume1.state == 'available':
                volume1.delete()
                break
            sleep(0.5)
        
        response = Result(
            detail={'msg':'delete {} success'.format(DeleteDiskIn["Device"])},
            status_code=200
            )   
        # response = Result(
        #     detail={'VolumeId':volume1.volume_id,
        #     "State" : volume1.state,
        #     },
        #     status_code=200
        #     )
        # response = Result(
        #     detail={'VolumeId':volume['VolumeId'],
        #     "State" : volume["State"],
        #     },
        #     status_code=200
        #     )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()




# class EBS_Volume(MethodView):
    # token 验证
    # decorators = [auth_required(auth_token)]
    # 创建EBS卷



@bp.put('/volume/attach')
@auth_required(auth_token)
def attach_server(parm):
    '''块存储关联云服务器(ec2)'''
    pass


@bp.put('/volume/detach')
@auth_required(auth_token)
def detach_server(parm):
    '''块存储分离云服务器(ec2)'''
    pass