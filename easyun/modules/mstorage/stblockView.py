import boto3
from datetime import date, timedelta
from flask import send_file
from flask.views import MethodView
from apiflask import auth_required, Schema
from apiflask.decorators import output, input
from apiflask.validators import Length
from marshmallow.fields import String, Integer, Boolean
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from .volume_schema import newVolume
from . import TYPE, bp, FLAG


# 将磁盘管理代码从服务器模块移到存储管理模块
   
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

@bp.post('/block/disk')
@auth_required(auth_token)
@input(NewDiskIn)
# @output()
def add_disk(NewDiskIn):
    '''增加磁盘'''
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


class DeleteDiskIn(Schema):
    svrId = String(required=True, example='i-0ac436622e8766a13')  #云服务器ID
    diskPath = String(required=True, example='/dev/sdg')


@bp.delete('/block/disk')
@auth_required(auth_token)
@input(DeleteDiskIn)
# @output()
def delete_disk(DeleteDiskIn):
    '''删除磁盘'''
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


class DiskOut(Schema):
   id = String()
   state = String()
   create_time = String()
   tags = String()
   
@bp.get('/block/disk')
@auth_required(auth_token)
@output(DiskOut)
def get_disk():
    '''获取available状态磁盘'''
    try:
        RESOURCE = boto3.resource('ec2')
        res = []
        for volume in RESOURCE.volumes.all():
            if volume.tags and [i for i in volume.tags if 'Easyun' in i['Value']]:
                print(volume.id,volume.state,volume.create_time,volume.tags)
                if volume.state=='available':
                    # print(volume.id,volume.state,volume.create_time,volume.tags)
                    res.append((volume.id,volume.state,volume.create_time,volume.tags))
        # print(res)
        response = Result(
            detail=res,
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


@bp.route("/block/volume")
class EBS_Volume(MethodView):
    # token 验证
    decorators = [auth_required(auth_token)]

    # 创建EBS卷
    @input(newVolume)
    def post(self, data):
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
                    'Tags' : [{ 'Key':'Flag','Value':FLAG }]
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