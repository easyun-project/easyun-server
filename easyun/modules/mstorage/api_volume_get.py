# encoding: utf-8
"""
  @module:  Block Storage Module
  @desc:    块存储(EBS) Volume 卷查询相关
  @auth:    
"""

from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.cloud.utils import set_boto3_region
from easyun.cloud.sdk_volume import StorageVolume
from .schemas import VolumeModel, VolumeBasic, VolumeDetail
from . import bp


_ST_VOLUME = None


def get_ST_VOLUME(dcName):
    global _ST_VOLUME
    if _ST_VOLUME is not None and _ST_VOLUME.dcName == dcName:
        return _ST_VOLUME
    else:
        return StorageVolume(dcName)


@bp.get('/volume')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(VolumeModel(many=True), description='All volume list (detail)')
def list_volume_detail(parm):
    '''获取数据中心全部块存储信息'''
    dcName = parm.get('dc')
    # 设置 boto3 接口默认 region_name
    dcRegion = set_boto3_region(dcName)
    try:
        # vol = StorageVolume(dcName)
        vol = get_ST_VOLUME(dcName)
        volumeList = vol.list_all_volume()

        resp = Result(detail=volumeList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=4101)
        return resp.err_resp()


@bp.get('/volume/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(VolumeBasic(many=True), description='All volume list (brief)')
def list_volume_brief(parm):
    '''获取数据中心全部块存储列表[仅基础字段]'''
    dcName = parm.get('dc')
    # 设置 boto3 接口默认 region_name
    dcRegion = set_boto3_region(dcName)
    try:
        # vol = StorageVolume(dcName)
        vol = get_ST_VOLUME(dcName)
        volumeList = vol.get_volume_list()

        resp = Result(detail=volumeList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=4102)
        return resp.err_resp()


@bp.get('/volume/<volume_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(VolumeDetail, description='A Volume Detail Info')
def get_volume_detail(volume_id, parm):
    '''获取指定块存储(Volume)详细信息'''
    dcName = parm.get('dc')
    # 设置 boto3 接口默认 region_name
    dcRegion = set_boto3_region(dcName)
    try:
        vol = get_ST_VOLUME(dcName)
        volumeDetail = vol.get_volume_detail(volume_id)

        response = Result(detail=volumeDetail, status_code=200)
        return response.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=4103)
        response.err_resp()
