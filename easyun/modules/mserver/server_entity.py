# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get info: Server list, Server detail
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from datetime import date, datetime
from . import bp, REGION, FLAG
from flask import jsonify


class DetailOut(Schema):
    ins_id = String()
    tag_name = Dict()
    ins_status = String()
    ins_type = String()
    vcpu = Integer()
    ram = String()
    subnet_id = String()
    ssubnet_id = String()
    key_name = String()
    category = String()


@bp.get('/detail/<svr_id>')
@auth_required(auth_token)
# @output(DetailOut, description='Server detail info')
def get_svr(svr_id):
    '''查看指定云服务器详情'''
    CLIENT = boto3.client('ec2', region_name=REGION)

    # Helper method to serialize datetime fields
    def json_datetime_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))

    response = CLIENT.describe_instances(InstanceIds=[svr_id])

    return response['Reservations']   


@bp.get('/instypes/<svr_id>')
# @auth_required(auth_token)
# @input()
# @output()
def get_types(svr_id):
    '''获取指定云服务器支持的Instance Types列表'''

    # 1.查询云服务器的架构 x86-64bit / arm-64bit

    # 2.查询相同架构下的Instance Types

    return ''