# -*- coding: utf-8 -*-
'''
@Description: Server Management - Modify: Name, Instance type, 
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict, Boolean
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.cloud.utils import query_dc_region, get_server_name
from .schemas import ModSvrNameParm, SvrTagNameItem
from . import bp, REGION



@bp.get('/name/<svr_id>')
@auth_required(auth_token)
# @input()
@output(SvrTagNameItem)
def get_svr_name(svr_id):
    '''查询指定云服务器的名称'''
    try:
        response = Result(
            detail={
                'svrId' : svr_id,
                'tagName' : get_server_name(svr_id)
            },
            status_code=200
            )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3101, http_status_code=400
        )
        response.err_resp()



@bp.put('/name')
# @auth_required(auth_token)
@input(ModSvrNameParm)
@output(SvrTagNameItem(many=True))
def update_svr_name(parms):
    '''修改指定云服务器名称'''
    try:
        nameTag = {'Key': 'Name', 'Value': parms["svrName"]}

        resource_ec2 = boto3.resource('ec2')

        svrList = []
        if len(parms['svrIds']) > 0:
            svrList = resource_ec2.instances.filter(
                InstanceIds=parms["svrIds"]
            )
            updateTags = svrList.create_tags(Tags = [nameTag] )

        response = Result(
            detail=[{
                'svrId' : server.id,
                'tagName' : next((tag['Value'] for tag in server.tags if tag["Key"] == 'Name'), None)
                } for server in svrList],
            status_code=200
        )
        return response.make_resp()
    except Exception as e:
        response = Result(
            message=str(e), status_code=3102, http_status_code=400
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
@auth_required(auth_token)
@input(ConfigIn)
# @output(UpdateOut)
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
                raise ValueError('Server must be stopped.')
            else:
                server.modify_attribute(
                    InstanceType={
                    'Value': new["ins_type"]
                    }
                )
                response = Result(
                    detail={'msg':'config success'},
                    status_code=200
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