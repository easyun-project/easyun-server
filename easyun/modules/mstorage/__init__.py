# -*- coding: utf-8 -*-
"""The Storage management module."""
from apiflask import APIBlueprint
from easyun.common.models import Account, Datacenter
from easyun.cloud.sdk_bucket import StorageBucket

# define api version
ver = '/api/v1'

bp = APIBlueprint('存储管理', __name__, url_prefix=ver + '/storage')


_ST_BUCKET = None


def get_storage_bucket(dcName):
    global _ST_BUCKET
    if _ST_BUCKET is not None and _ST_BUCKET.dcName == dcName:
        return _ST_BUCKET
    else:
        _ST_BUCKET = StorageBucket(dcName)
        return _ST_BUCKET


from . import (
    api_mock,
    api_bucket_get,
    api_bucket_mgt,
    api_object_mgt,
    api_volume_get,
    api_volume_mgt,
)
