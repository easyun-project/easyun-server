# -*- coding: utf-8 -*-
"""The Storage management module."""

from apiflask import APIBlueprint, auth_required
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result
from easyun.common.schemas import RegionModel
from easyun.cloud import get_cloud
from easyun.cloud.aws.workload import StorageBucket
from easyun.cloud.aws.resources import StorageVolume


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


@bp.get('/s3-region')
@auth_required(auth_token)
@bp.output(RegionModel(many=True), description='Get Region List')
def list_s3_region():
    '''获取S3可用的Region列表'''
    try:
        thisAccount: Account = Account.query.first()
        cloud = get_cloud(thisAccount.account_id, thisAccount.aws_type)

        regionList = cloud.get_region_list('s3')

        resp = Result(detail=regionList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=2005)
        response.err_resp()


from . import api_bucket_mgt, api_volume_mgt


bp.register_blueprint(api_bucket_mgt.bp)
bp.register_blueprint(api_volume_mgt.bp)
