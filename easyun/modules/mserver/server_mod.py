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



@bp.get('/name/<svr_id>')
@auth_required(auth_token)
# @input()
# @output()
def get_svr_name(svr_id):
    '''查询指定云服务器的名称'''
    try:
        resource_ec2 = boto3.resource('ec2', region_name = REGION)
        server = resource_ec2.Instance(svr_id)
        nameTag = [tag['Value'] for tag in server.tags if tag['Key'] == 'Name']
        response = Result(
            detail={
                'Svr_Id' : svr_id,
                'Svr_Name' : nameTag[0]
            },
            status_code=200
            )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3001, http_status_code=400
        )
        response.err_resp()


@bp.put('/name')
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


@bp.post('/config')
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


# @bp.get('/instypes/<svr_id>')
# @auth_required(auth_token)
# # @input()
# # @output()
# def get_ins_types(svr_id):
#     '''查询指定云服务器的实例配置'''
#     RESOURCE = boto3.resource('ec2', region_name=REGION)
#     # 1.查询云服务器的架构 x86-64bit / arm-64bit
#     server = RESOURCE.Instance(svr_id)


    
    # 2.查询相同架构下的Instance Types