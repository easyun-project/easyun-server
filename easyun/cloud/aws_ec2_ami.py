# -*- coding: utf-8 -*-
"""
  @module:  AWS EC2 Images (AMI)
  @desc:    Define basic attributes of AWS EC2 in this file.  
  @auth:    aleck
"""

import boto3
from easyun.libs.utils import load_json_config
from easyun.cloud.aws_price import get_attribute_values


# 获取 windows ami 列表
AMI_Windows = load_json_config('aws_ec2_ami').get('windows')

# 获取 linux ami 列表
AMI_Linux = load_json_config('aws_ec2_ami').get('linux')

# 全部受支持的 AMI Operating System 列表
OperatingSystemALL = get_attribute_values('AmazonEC2','operatingSystem')



def split_ami_name(imgName, platform):
    '''根据系统平台从image name中截取有意义字段'''
    if platform == 'windows':
        pass
    elif platform == 'linux':
        pass
    return ''
    