# -*- coding: utf-8 -*-
'''
@Description: Server Management - Modify: Name, Instance type, 
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from flask import jsonify
from werkzeug.wrappers import response
from easyun.common.auth import auth_token
from easyun.common.result import make_resp, error_resp, bad_request, Result
from . import bp, REGION, FLAG


class NewNameIn(Schema):
    svr_ids = List(         #云服务器ID
        String(),
        required=True,
        example=['i-01b565d505d5e0559']
    )
    svr_name = String(
        required=True,
        example='new_server_name'
    )

class UpdateOut(Schema):
    svr_ids = List(String) 

@bp.post('/mod-name')
# @auth_required(auth_token)
@input(NewNameIn)
@output(UpdateOut)
def update_name(new):
    '''修改指定云服务器名称'''
    TAGS = [
        {'Key': 'Name', 'Value': new["svr_name"]}
    ]
    RESOURCE = boto3.resource('ec2', region_name=REGION)
    servers = RESOURCE.instances.filter(
        InstanceIds=new["svr_ids"]
        )
    update_result = servers.create_tags(Tags=TAGS)
    response = Result(
        detail={'svr_ids':[i.InstanceId for i in update_result]},
        status_code=3000
        )
    return response.make_resp()



class NewConfigIn(Schema):
    svr_ids = List(         #云服务器ID
        String(),
        required=True,
        example=['i-01b565d505d5e0559']
    )
    ins_type = String(
        required=True,
        example='t3.small'
    )


@bp.post('/mod-config')
# @auth_required(auth_token)
@input(NewConfigIn)
@output(UpdateOut)
def update_cfg(new):
    '''修改指定云服务器配置'''
    RESOURCE = boto3.resource('ec2', region_name=REGION)
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
