# -*- coding: utf-8 -*-
"""The Storage management module."""
from apiflask import APIBlueprint
from easyun.common.models import Account, Datacenter

# define api version
ver = '/api/v1'

bp = APIBlueprint('存储管理', __name__, url_prefix = ver+'/storage') 

TYPE = 'AWS::S3::Bucket'

FLAG = "Easyun"

REGION = "us-east-1"

from . import api_mock, api_bucket_get, api_bucket_mgt, api_bucket_entity ,api_object_mgt ,api_object_get ,api_volume_get, api_volume_mgt