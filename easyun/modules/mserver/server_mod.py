# -*- coding: utf-8 -*-
'''
@Description: Server Management - Modify: Name, Instance type, 
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict, Boolean
from apiflask.validators import Length, OneOf
from flask import jsonify
from marshmallow.utils import pprint
from werkzeug.wrappers import response
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.result import make_resp, error_resp, bad_request, Result
from . import bp, REGION


class NewNameIn(Schema):
    svr_ids = List(         #云服务器IDs
        String(),
        required=True,
        example=['i-01b565d505d5e0559']
    )
    svr_name = String(         #云服务器新Name
        required=True,
        example='new_server_name'
    )

class UpdateOut(Schema):
    svr_ids = List(String)
    new_name = List(String)

@bp.post('/mod_name')
# @auth_required(auth_token)
@input(NewNameIn)
# @output(UpdateOut)
def update_svr_name(NewNameIn):
    '''修改指定云服务器名称'''
    try:
        name_tag = [
            {'Key': 'Name', 'Value': NewNameIn["svr_name"]}
        ]
        resource_ec2 = boto3.resource('ec2', region_name=REGION)
        servers = resource_ec2.instances.filter(
            InstanceIds=NewNameIn["svr_ids"]
            )
        update_resp = servers.create_tags(Tags = name_tag )

        response = Result(
            # detail={'svr_ids':[i.InstanceId for i in update_result]},
            detail=[{
                'Svr_Id' : server.id,
                'New_Name' : [tag['Value'] for tag in server.tags if tag['Key'] == 'Name'][0]
                } for server in servers],
            status_code=200
            )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()  



@bp.get('/svrname/<server_id>')
@auth_required(auth_token)
# @input()
# @output()
def get_svr_name(server_id):
    '''查询指定云服务器的名称'''
    try:
        resource_ec2 = boto3.resource('ec2', region_name = REGION)
        server = resource_ec2.Instance(server_id)
        svr_name = [tag['Value'] for tag in server.tags if tag['Key'] == 'Name']
        response = Result(
            detail={
                'Svr_Id' : server_id,
                'Svr_Name' : svr_name[0]
            },
            status_code=200
            )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()
    

    
    # 2.查询相同架构下的Instance Types

    # response = Result(
    #     detail={'svr_ids':[i.InstanceId for i in update_result]},
    #     status_code=3000
    #     )
    # return response.make_resp()


class ConfigIn(Schema):
    svr_ids = List(         #云服务器ID
        String(),
        required=True,
        example=['i-01b565d505d5e0559']
    )
    ins_type = String(
        required=True,
        example='t3.small'
    )


@bp.post('/mod_config')
# @auth_required(auth_token)
@input(ConfigIn)
@output(UpdateOut)
def update_config(new):
    '''修改指定云服务器实例配置'''
    try: 
        RESOURCE = boto3.resource('ec2', region_name=REGION)
        ####有的实例是没有subnet_id的
        servers = RESOURCE.instances.filter(
            InstanceIds=new["svr_ids"]
        )
        # 判断服务器是否处于关机状态
        for server in servers:
            if server.state["Name"] != "stopped":
                response = Result(
                message='Server must be stopped.', status_code=3000,http_status_code=400
                )
                response.err_resp()
        update_result = servers.modify_attribute(
            InstanceType={
            'Value': new["ins_type"]
            }
        )
        response = Result(
            detail={'svr_ids':[i.InstanceId for i in update_result]},
            status_code=3000
            )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()

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

@bp.post('/disk/add')
# @auth_required(auth_token)
@input(NewDiskIn)
# @output()
def add_disk(NewDiskIn):
    '''增加磁盘'''
    try:
        CLIENT = boto3.client('ec2', region_name=REGION)
        RESOURCE = boto3.resource('ec2', region_name=REGION)
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
    InstanceId = String(required=True, example='i-0ac436622e8766a13')  #云服务器ID
    Device = String(required=True, example='/dev/sdg')

@bp.post('/disk/delete')
# @auth_required(auth_token)
@input(DeleteDiskIn)
# @output()
def delete_disk(DeleteDiskIn):
    '''删除磁盘'''
    try:
        CLIENT = boto3.client('ec2', region_name=REGION)
        RESOURCE = boto3.resource('ec2', region_name=REGION)
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
                # volume1.delete()
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


# @bp.get('/instypes/<server_id>')
# @auth_required(auth_token)
# # @input()
# # @output()
# def get_ins_types(server_id):
#     '''查询指定云服务器的实例配置'''
#     RESOURCE = boto3.resource('ec2', region_name=REGION)
#     # 1.查询云服务器的架构 x86-64bit / arm-64bit
#     server = RESOURCE.Instance(server_id)


    
    # 2.查询相同架构下的Instance Types