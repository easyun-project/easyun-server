# -*- coding: utf-8 -*-
'''
@Description: Server Management - Get Server Parameters, like: AMI id,instance type
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



@bp.get('/list_amis')
# @auth_required(auth_token)
# @input()
# @output()
def list_amis():
    '''获取当前region下指定参数的AMIs列表'''

    # x86-64bit / arm-64bit
    # Linux(8) / Windows(4)

    return ''



@bp.get('/list_types')
# @auth_required(auth_token)
# @input()
# @output()
def list_types():
    '''获取当前region下指定参数的Instance Types列表'''
    return ''


@bp.get('/get_types')
# @auth_required(auth_token)
# @input()
# @output()
def get_types():
    '''获取当前服务器支持的Instance Types列表'''

    # 1.查询云服务器的架构 x86-64bit / arm-64bit
    # 2.查询相同架构下的Instance Types

    return ''
