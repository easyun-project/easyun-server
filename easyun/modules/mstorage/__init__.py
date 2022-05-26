# -*- coding: utf-8 -*-
"""The Storage management module."""
from apiflask import APIBlueprint
from easyun.cloud.aws.resources import StorageVolume, StorageBucket


# define api version
ver = '/api/v1'

bp = APIBlueprint('存储管理', __name__, url_prefix=ver + '/storage')

_ST_VOLUME = None
_ST_BUCKET = None


def get_st_volume(dcName):
    global _ST_VOLUME
    if _ST_VOLUME is not None and _ST_VOLUME.dcName == dcName:
        return _ST_VOLUME
    else:
        return StorageVolume(dcName)


def get_st_bucket(dcName):
    global _ST_BUCKET
    if _ST_BUCKET is not None and _ST_BUCKET.dcName == dcName:
        return _ST_BUCKET
    else:
        return StorageBucket(dcName)


from . import (
    api_mock,
    api_bucket_get,
    api_bucket_mgt,
    api_object_mgt,
    api_volume_get,
    api_volume_mgt,
)
