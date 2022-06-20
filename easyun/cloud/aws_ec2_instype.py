# -*- coding: utf-8 -*-
"""
  @module:  AWS ec2 instance types
  @desc:    Define basic attributes of AWS EC2 in this file.
  @auth:    aleck
"""
from easyun.libs.utils import load_json_config
from easyun.cloud.aws_price import get_attribute_values


# 获取 EC2 Instance Family 列表
Instance_Family = load_json_config('aws_ec2_family')

'''全部受支持的Instance Tpye列表'''
InstanceTypeALL = get_attribute_values('AmazonEC2', 'instanceType')


def get_family_descode(parm):
    '''获取Instance Family描述信息'''
    for i in Instance_Family:
        familyDes = [
            f['familyDes'] for f in i['familyList'] if f.get('familyName') == parm
        ]
        if familyDes:
            return familyDes[0]
    if not familyDes:
        return parm + ' Instance'
