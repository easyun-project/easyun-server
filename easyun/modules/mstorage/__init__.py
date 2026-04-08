# -*- coding: utf-8 -*-
"""The Storage management module."""

from apiflask import APIBlueprint
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result
from easyun.common.schemas import RegionModel
from easyun.cloud import get_cloud


# define api version
ver = '/api/v1'

bp = APIBlueprint('存储管理', __name__, url_prefix=ver + '/storage')


@bp.get('/s3-region')
@bp.auth_required(auth_token)
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
