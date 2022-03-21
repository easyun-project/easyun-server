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
from easyun.common.result import Result
from .schemas import SvrIdList, SvrOperateOut
from . import bp


class OperateIn(Schema):
    svr_ids = List(         #云服务器ID
        String(),
        required=True
    )
    action = String(
        required=True, 
        validate=OneOf(['start', 'stop', 'restart'])  #Operation TYPE
        )   




@bp.post('/action')
@auth_required(auth_token)
@input(OperateIn)
# @output(SvrOperateOut, description='Operation finished !')
def operate_svr(operate):
    '''启动/停止/重启 云服务器'''
    # print(operate)
    try:
        resource_ec2 = boto3.resource('ec2')
        servers = resource_ec2.instances.filter(
            InstanceIds=operate["svr_ids"]
            )
        operation_results = []
        if operate["action"] == 'restart':
            for server in servers:
                if server.state['Name'] == "running":
                    server.reboot()
                else:
                    raise ValueError('server state is not running')
            operation_results = "restart server success"
        else:
            for server in servers:
                # print(server)
                if operate["action"] == 'start':
                    operation_result = server.start()
                elif operate["action"] == 'stop':
                    operation_result = server.stop()
                key = [i for i in operation_result.keys() if i !="ResponseMetadata"][0]
                res = operation_result[key][0]
                tmp = {
                    'svrId':res.get('InstanceId'),
                    'currState':res['CurrentState'].get('Name'),
                    'preState':res['PreviousState'].get('Name')
                }
                operation_results.append(tmp)
        print(operation_results)
        resp = Result(
            detail=operation_results,
            status_code=200,
        )
        return resp.make_resp()
    except Exception as e:
        resp = Result(
            message=str(e), 
            # message='{} server failed'.format(operate["action"]), 
            status_code=3004,
            http_status_code=400
        )
        resp.err_resp()



@bp.delete('')
@auth_required(auth_token)
@input(SvrIdList)
# @output(SvrOperateOut, description='Operation finished !')
def delete_svr(parm):
    '''删除(Terminate)云服务器'''
    try:
        resource_ec2 = boto3.resource('ec2')
        servers = resource_ec2.instances.filter(
            InstanceIds=parm["svrIds"],
            # Filters=[
            # {'Name': 'tag:Flag','Values': [FLAG]}
            # ]            
        )
        deleteList = []
        for server in servers:
            termResp = server.terminate()
            # server.wait_until_terminated()
            termInst = termResp.get('TerminatingInstances')[0]
            tmp = {
                'svrId':termInst.get('InstanceId'),
                'currState':termInst['CurrentState'].get('Name'),
                'preState':termInst['PreviousState'].get('Name')
            }
            deleteList.append(tmp)


        resp = Result(
            detail=deleteList,
            status_code=200,
        )
        return resp.make_resp()

    except Exception:
        resp = Result(
            message='Delete server failed', 
            status_code=3004, 
            http_status_code=400
        )
        return resp.err_resp()