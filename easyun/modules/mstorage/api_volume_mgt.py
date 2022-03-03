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
    dcName = String(required=True, example="Easyun")
    volumeSize = Integer(required=True, example=10)
    volumeType = String(required=True, example='gp3')
    isEncrypted = Boolean(required=True, example = False) 
    volumeIops = Integer(example=3000)
    volumeThruput = Integer( example=500) 
    tagName = String(example='disk_test')
    azName = String(example='us-east-1a')
    svrId = String(example='i-0ac436622e8766a13')  #云服务器ID  
    attachPath = String(example='/dev/sdg')  


@bp.post('/volume')
@auth_required(auth_token)
@input(NewDiskIn)
# @output()
def add_disk(parms):
    '''新增磁盘(EBS Volume)'''
    dcName = parms['dcName']
    try:
        CLIENT = boto3.client('ec2')
        resource_ec2 = boto3.resource('ec2')
        if parms.get("svrId"):
            thisSvr = resource_ec2.Instance(parms.get("svrId"))
            azName = resource_ec2.Subnet(thisSvr.subnet_id).availability_zone,
        else:
            azName = parms.get('azName')
        TagSpecifications = [
            {
                "ResourceType":"volume",
                "Tags": [
                        {"Key": "Flag", "Value": dcName},
                        {"Key": "Name", "Value": parms.get('tagName')}
                    ]
            }
        ]
        volumeIops = parms.get('volumeIops')
        volumeThruput = parms.get('volumeThruput')

        if volumeIops and not volumeThruput:
            volume = CLIENT.create_volume(
                AvailabilityZone = azName,
                Encrypted= parms['isEncrypted'],
                Size=parms['volumeSize'],
                VolumeType=parms['volumeType'],             
                TagSpecifications=TagSpecifications,
                Iops = volumeIops                
            )
        elif not volumeIops and volumeThruput:
            volume = CLIENT.create_volume(
                AvailabilityZone = azName,
                Encrypted= parms['isEncrypted'],
                Size=parms['volumeSize'],
                VolumeType=parms['volumeType'],             
                TagSpecifications=TagSpecifications,
                Throughput= volumeThruput,
            )
        else:
            volume = CLIENT.create_volume(
                AvailabilityZone = azName,
                Encrypted= parms['isEncrypted'],
                Size=parms['volumeSize'],
                VolumeType=parms['volumeType'],             
                TagSpecifications=TagSpecifications,
                Iops = volumeIops,
                Throughput= volumeThruput,
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
        #     Device=parms["Device"],
        #     InstanceId=parms["InstanceId"]
        # )
        from time import sleep 
        if parms.get("attachPath"):
            thisDisk = resource_ec2.Volume(volume['VolumeId'])
            if thisDisk.state == 'available':
                thisDisk.attach_to_instance(
                    Device=parms["attachPath"],
                    InstanceId=parms["SvrId"]
                )
                
            sleep(0.5)
            
        response = Result(
            detail={
                'volumeId':thisDisk.volume_id,
                'volueState' : thisDisk.state,
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