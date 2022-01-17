# -*- coding: utf-8 -*-
'''
@Description: Server Management - action: start, restart, stop, delete; and get status
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.schemas import EmptySchema
from apiflask.validators import Length, OneOf
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from . import bp, REGION
from os import abort


class OperateIn(Schema):
    svr_ids = List(         #云服务器ID
        String(),
        required=True
    )
    action = String(
        required=True, 
        validate=OneOf(['start', 'stop', 'restart'])  #Operation TYPE
        )   


class OperateOut(Schema):
    svr_ids = List(String) 

@bp.post('/action')
@auth_required(auth_token)
@input(OperateIn)
@output(OperateOut, description='Operation finished !')
def operate_svr(operate):
    '''启动/停止/重启 云服务器'''
    print(operate)
    try:
        RESOURCE = boto3.resource('ec2', region_name=REGION)
        servers = RESOURCE.instances.filter(
            InstanceIds=operate["svr_ids"]
            )
        print(servers)
        servers.stop()
        if operate["action"] == 'start':
            operation_result = servers.start()
        elif operate["action"] == 'stop':
            operation_result = servers.stop()
        else:
            operation_result = servers.restart()
        response = Result(
            detail={'svr_ids':[i.InstanceId for i in operation_result]},status_code=200,
        )
        return response.make_resp()
    except Exception:
        response = Result(
            message='{} server failed'.format(operate["action"]), status_code=3004,http_status_code=400
        )
        response.err_resp()



class DeleteIn(Schema):
    svr_ids = List(         #云服务器ID
        String(),
        required=True
    )
    action = String(
        required=True, 
        validate=OneOf(['delete'])  #Operation TYPE
        )   


@bp.delete('/')
@auth_required(auth_token)
@input(DeleteIn)
@output(OperateOut)
def del_svr(operate):
    '''删除指定云服务器'''
    try:
        RESOURCE = boto3.resource('ec2', region_name=REGION)   
        servers = RESOURCE.instances.filter(
            InstanceIds=operate["svr_ids"],
            Filters=[
            {'Name': 'tag:Flag','Values': [FLAG]}
            ]
        )
        for server in servers:
            response = server.terminate()
            # server.wait_until_terminated()
        return response

        response = Result(
            detail={'svr_ids':[i.InstanceId for i in operation_result]},status_code=200,
        )
        return response.make_resp()

    except Exception:
        response = Result(
            message='{} server failed'.format(operate["action"]), status_code=3004, http_status_code=400
        )
        response.err_resp()