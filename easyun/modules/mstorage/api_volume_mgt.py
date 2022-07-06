# encoding: utf-8
"""
  @module:  Block Storage Module
  @desc:    块存储(EBS) Volume 卷管理相关
  @auth:    aleck
"""

import boto3
from apiflask import APIBlueprint, auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.cloud.aws import get_datacenter
from easyun.cloud.aws.workload import get_st_volume, get_ec2_server
from easyun.cloud.utils import get_disk_type
from .schemas import (
    VolumeModel,
    VolumeBasic,
    VolumeDetail,
    AddVolumeParm,
    DelVolumeParm,
    AttachVolParm,
    DetachVolParm,
)


bp = APIBlueprint('Volume', __name__, url_prefix='/volume')


# 定义系统盘路径
SystemDisk = ['/dev/xvda', '/dev/sda1']


@bp.get('')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(VolumeModel(many=True), description='All volume list (detail)')
def list_volume_detail(parm):
    '''获取数据中心全部块存储信息'''
    dcName = parm.get('dc')
    # 设置 boto3 接口默认 region_name
    # dcRegion = set_boto3_region(dcName)
    try:
        # vol = get_st_volume(dcName)
        # volumeList = vol.list_all_volume()
        dc = get_datacenter(dcName)
        volumeList = dc.resources.list_all_volume()

        resp = Result(detail=volumeList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=4101)
        return resp.err_resp()


@bp.get('/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(VolumeBasic(many=True), description='All volume list (brief)')
def list_volume_brief(parm):
    '''获取数据中心全部块存储列表[仅基础字段]'''
    dcName = parm.get('dc')
    # 设置 boto3 接口默认 region_name
    # dcRegion = set_boto3_region(dcName)
    try:
        # vol = StorageVolume(dcName)
        # vol = get_st_volume(dcName)
        # volumeList = vol.get_volume_list()
        dc = get_datacenter(dcName)
        volumeList = dc.resources.get_volume_list()

        resp = Result(detail=volumeList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=4102)
        return resp.err_resp()


@bp.get('/<volume_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(VolumeDetail, description='A Volume Detail Info')
def get_volume_detail(volume_id, parm):
    '''获取指定块存储(Volume)详细信息'''
    dcName = parm.get('dc')
    # 设置 boto3 接口默认 region_name
    # dcRegion = set_boto3_region(dcName)
    try:
        vol = get_st_volume(dcName)
        volumeDetail = vol.get_detail(volume_id)

        response = Result(detail=volumeDetail, status_code=200)
        return response.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=4103)
        response.err_resp()


@bp.post('')
@auth_required(auth_token)
@bp.input(AddVolumeParm)
@bp.output(VolumeModel)
def add_volume(parms):
    '''新增磁盘(EBS Volume)'''
    dcName = parms.pop('dcName')
    svrId = parms.pop('svrId')
    attachPath = parms.pop('attachPath')
    try:
        # 如果传入了svrID，则从该server上获取相关属性
        if svrId:
            thisSvr = get_ec2_server(svrId)
            # 获取 server az属性
            volumeZone = thisSvr.svrObj.placement.get('AvailabilityZone')
            # 以 server tagName 作为卷名前缀
            diskType = get_disk_type(attachPath) if attachPath else 'disk'
            tagName = '%s-%s' % (thisSvr.tagName, diskType)
        else:
            volumeZone = parms.get('azName')
            tagName = parms.get('tagName')
        dc = get_datacenter(dcName)
        newVolume = dc.workload.create_volume(
            vol_type=parms['volumeType'],
            vol_size=parms['volumeSize'],
            vol_zone=volumeZone,
            iops=parms['volumeIops'],
            throughput=parms['volumeThruput'],
            is_multiattach=parms['isMultiAttach'],
            is_encrypted=parms['isEncrypted'],
            tag_name=tagName,
        )
        volItem = {
            'volumeId': newVolume.id,
            'volumeState': newVolume.volObj.state,
            'createTime': newVolume.volObj.create_time,
            'volumeAz': newVolume.volObj.availability_zone,
        }
        # 如果传入了svrID和 attachPath参数，则将volume挂载到server上
        if svrId and attachPath:
            attachResp = thisSvr.svrObj.attach_volume(
                Device=[attachPath], VolumeId=newVolume.id
            )
            # 返回增加 volume attachment相关信息
            volAttach = {
                # 获取 volume状态更新
                'volumeState': attachResp['State'],
                'volumeAttach': [
                    {
                        'attachSvrId': svrId,
                        'attachSvr': thisSvr.tagName,
                        'attachPath': attachPath,
                        'diskType': diskType,
                    }
                ],
            }
            volItem.update(volAttach)
        resp = Result(
            detail=volItem,
            status_code=201,
        )
        return resp.make_resp()

    except Exception as e:
        response = Result(message=str(e), status_code=5001, http_status_code=400)
        response.err_resp()


@bp.delete('')
@auth_required(auth_token)
@bp.input(DelVolumeParm)
def del_volume(parm):
    '''删除磁盘(EBS Volume)'''
    try:
        # dcRegion = set_boto3_region(dcName)
        resource_ec2 = boto3.resource('ec2')
        deleteList = []
        for volumeId in parm['volumeIds']:
            thisVol = resource_ec2.Volume(volumeId)
            # 判断 volume state
            if thisVol.state == 'available':
                thisVol.delete()  # Returns  None
                deleteResult = {volumeId: 'success deleted'}
            else:
                deleteResult = {volumeId: 'failed, volume in-use'}
            deleteList.append(deleteResult)

        response = Result(detail=deleteList, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=5001, http_status_code=400)
        response.err_resp()


@bp.put('/attach')
@bp.input(AttachVolParm)
@auth_required(auth_token)
def attach_server(parm):
    '''块存储关联云服务器(ec2)【ToBeFix】'''
    resource_ec2 = boto3.resource('ec2')
    thisVol = resource_ec2.Volume(parm['volumeId'])
    # 判断 volume state
    if thisVol.state == 'Available':
        diskType = 'system' if parm['attachPath'] in SystemDisk else 'user'
    if thisVol.state == 'In-use':
        detachResult = thisVol.attach_to_instance(
            InstanceId=parm["svrId"],
            Device=parm["attachPath"],
        )

        # 返回增加 volume attachment相关信息
        volResp = {
            'attachSvr': parm["svrId"],
            'attachPath': parm["attachPath"],
            'diskType': diskType,
            # 获取 volume状态更新
            'volumeState': detachResult['State'],
        }
    else:
        raise

    response = Result(detail=volResp, status_code=200)
    return response.make_resp()


@bp.put('/detach')
@bp.input(DetachVolParm)
@auth_required(auth_token)
def detach_server(parm):
    '''块存储分离云服务器(ec2)【ToBeFix】'''
    resource_ec2 = boto3.resource('ec2')
    thisVol = resource_ec2.Volume(parm['volumeId'])
    # 判断 volume state
    if thisVol.state == 'In-use':
        detachResult = thisVol.detach_from_instance(
            InstanceId=parm["svrId"],
            Device=parm["attachPath"],
        )
    else:
        raise

    response = Result(detail=detachResult, status_code=200)
    return response.make_resp()
