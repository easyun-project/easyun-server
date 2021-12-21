# -*- coding: utf-8 -*-
'''
@Description: Server Management - Add new server
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.schemas import EmptySchema 
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from . import bp, REGION



# 测试用云服务器参数示例
Svrargs = {
    "Number" : 1,
    "ImageId" : "ami-083654bd07b5da81d",
    "InstanceType" : "t3.nano",
    "SubnetId" : "subnet-06bfe659f6ecc2eed",
    "SecurityGroupIds" : ["sg-05df5c8e8396d06e9",],
    "KeyName" : "key_easyun_dev",
    "BlockDeviceMappings" : [
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {            
                "DeleteOnTermination": True,
                "VolumeSize": 16,
                "VolumeType": "gp2"
                }
        },
        {
            "DeviceName": "/dev/sdf",
            "Ebs": {            
                "DeleteOnTermination": True,
                "VolumeSize": 13,
                "VolumeType": "gp2"
                } 
        }
    ],
    "TagSpecifications" : [
        {
        "ResourceType":"instance",
        "Tags": [
                {"Key": "Flag", "Value": "Easyun"},
                {"Key": "Name", "Value": "test-from-api"}
            ]
        }
        ]
}

class SvrParmIn(Schema):
    name = String(                          #云服务器名称
        required=True, 
        validate=Length(0, 30),
        example="server_name"
    ) 
    Number = Integer(required=True, example=1)            #新建云服务器数量
    ImageId = String(required=True, example="ami-083654bd07b5da81d")          #ImageId
    InstanceType = String(required=True,example="t3.nano")            #INSTANCE_TYPE
    SubnetId = String(required=True,example="subnet-06bfe659f6ecc2eed") 
    SecurityGroupIds = List(String(required=True ,example= "sg-05df5c8e8396d06e9"))
    KeyName = String(required=True,example="key_easyun_dev")
    BlockDeviceMappings = List(
        Dict(
            example={
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "VolumeType": "gp2",
                    "VolumeSize": 16
                }
            }
        ),
        required=True
    )


class NewSvrSchema(Schema):
    NewSvrId = String()

# 新增server
@bp.post('/add')
@auth_required(auth_token)
@input(SvrParmIn)
# @output(NewSvrSchema)
def add_server(newsvr):
    '''新建云服务器'''
    try:
        # print(newsvr)
        TagSpecifications = [
        {
        "ResourceType":"instance",
        "Tags": [
                {"Key": "Flag", "Value": "Easyun"},
                {"Key": "Name", "Value": newsvr['name']}
            ]
        }
        ]
        RESOURCE = boto3.resource('ec2', region_name=REGION)
        # server = RESOURCE.create_instances(newsvr)
        servers = RESOURCE.create_instances(
            MaxCount = newsvr['Number'],
            MinCount = newsvr['Number'],
            ImageId = newsvr['ImageId'],
            InstanceType = newsvr['InstanceType'],
            SubnetId = newsvr['SubnetId'],
            SecurityGroupIds = newsvr['SecurityGroupIds'],
            # SecurityGroupIds = Svrargs['SecurityGroupIds'],
            KeyName = newsvr['KeyName'],
            BlockDeviceMappings = newsvr['BlockDeviceMappings'],
            # TagSpecifications = newsvr['TagSpecifications'],   
            TagSpecifications = TagSpecifications,   
            # BlockDeviceMappings = Svrargs['BlockDeviceMappings'],
            # TagSpecifications = Svrargs['TagSpecifications']    
        )
            
        response = Result(
            # detail = servers,
            detail=[{
                'SvrId' : server.id,
                'InsTpye' : server.instance_type,
                'CreateTime' : server.launch_time,                
                'State' : server.state["Name"],
                'PriIP' : server.private_ip_address
            } for server in servers],
            status_code=200
        )
        # server = [{'id':'3131442142'}]
        # response = Result(
        #     detail={'NewSvrId':server[0]['id']}, status_code=3001
        # )

        return response.make_resp()
    except Exception:
        response = Result(
            message='server creation failed', status_code=3001,http_status_code=400
        )
        response.err_resp()
