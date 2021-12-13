# -*- coding: utf-8 -*-
"""The Storage management module."""
import boto3
from apiflask import APIBlueprint
from easyun.common.models import Account, Datacenter

# define api version
ver = '/api/v1.0'

bp = APIBlueprint('存储管理', __name__, url_prefix = ver) 

CLIENT = boto3.client('cloudcontrol')

TYPE = 'AWS::S3::Bucket'

FLAG = "Easyun"