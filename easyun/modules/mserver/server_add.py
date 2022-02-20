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
from easyun.common.models import Datacenter
from easyun.common.result import Result, make_resp, error_resp, bad_request
from . import bp, REGION


class SvrParmIn(Schema):
    # datacenter basic parm
    dcName = String(required=True, example="Easyun")
    # parameters for server
    tagName = String(                          #云服务器名称
        required=True, 
        validate=Length(0, 40),
        example="dev_server_1"
    )
    svrNumber = Integer(required=True, example=1)            #新建云服务器数量
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


@bp.post('')
@auth_required(auth_token)
@input(SvrParmIn)
# @output(NewSvrSchema)
def add_server(parm):
    '''新建云服务器(EC2)'''
    flagTag = {"Key": "Flag", "Value": parm['dcName']}
    nameTag = {"Key": "Name", "Value": parm['tagName']}

    try:
        thisDC = Datacenter.query.filter_by(name = parm['dcName']).first()
        dcRegion = thisDC.get_region()

        resource_ec2 = boto3.resource('ec2', region_name = dcRegion)
        servers = resource_ec2.create_instances(
            MaxCount = parm['svrNumber'],
            MinCount = parm['svrNumber'],
            ImageId = parm['ImageId'],
            InstanceType = parm['InstanceType'],
            SubnetId = parm['SubnetId'],
            SecurityGroupIds = parm['SecurityGroupIds'],
            # SecurityGroupIds = Svrargs['SecurityGroupIds'],
            KeyName = parm['KeyName'],
            BlockDeviceMappings = parm['BlockDeviceMappings'],
            TagSpecifications = [
                {
                "ResourceType":"instance",
                "Tags": [flagTag, nameTag]
                },
                {
                "ResourceType":"volume",
                "Tags": [flagTag, nameTag]
                }
            ] 
        )
        svrList = [
            {
                'svrId' : server.id,
                'insTpye' : server.instance_type,
                'createTime' : server.launch_time.isoformat(),                
                'svrState' : server.state["Name"],
                'priIp' : server.private_ip_address
            } for server in servers]

        resp = Result(
            detail = svrList,
            status_code=200
        )
        return resp.make_resp()
        
    except Exception as ex:
        response = Result(
            detail=ex,
            message='server creation failed', 
            status_code=3001
        )
        return response.err_resp()
