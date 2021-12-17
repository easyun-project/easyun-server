# -*- coding: utf-8 -*-
"""The Storage management module."""
from apiflask import APIBlueprint
from easyun.common.models import Account, Datacenter

# define api version
ver = '/api/v1.0'

bp = APIBlueprint('存储管理', __name__, url_prefix = ver+'/storage') 

TYPE = 'AWS::S3::Bucket'

FLAG = "Easyun"

REGION = "us-east-1"

from . import bucket_add, bucket_list