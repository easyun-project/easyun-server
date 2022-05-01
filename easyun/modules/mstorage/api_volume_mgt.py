# encoding: utf-8
"""
  @module:  Block Storage Module
  @desc:    块存储(EBS) Volume 卷管理相关
  @auth:    
"""

import boto3
from apiflask import auth_required, Schema, input, output
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.cloud.utils import (
    gen_dc_tag,
    query_dc_region,
    get_server_name,
    set_boto3_region,
)
from .schemas import (
    VolumeDetail,
    AddVolumeParm,
    DelVolumeParm,
    AttachVolParm,
    DetachVolParm,
)
from . import bp


# 定义系统盘路径
SystemDisk = ['/dev/xvda', '/dev/sda1']


@bp.post('/volume')
@auth_required(auth_token)
@bp.input(AddVolumeParm)
@bp.output(VolumeDetail)
def add_volume(parms):
    '''新增磁盘(EBS Volume)'''
    dcName = parms['dcName']
    flagTag = gen_dc_tag(dcName)
    try:
        dcRegion = set_boto3_region(dcName)
        client_ec2 = boto3.client('ec2')
        resource_ec2 = boto3.resource('ec2')
        # volume attributes
        volumeType = parms['volumeType']
        volumeIops = parms.get('volumeIops')
        volumeThruput = parms.get('volumeThruput')
        isMultiAttach = parms.get('isMultiAttach')
        # attachment related attributes
        svrId = parms.get("svrId")
        attachPath = parms.get("attachPath")
        diskType = 'system' if attachPath in SystemDisk else 'user'

        # 如果传入了svrID，则从该server上获取相关属性
        if svrId:
            thisSvr = resource_ec2.Instance(svrId)
            # 获取 server az属性
            volumeAz = resource_ec2.Subnet(thisSvr.subnet_id).availability_zone
            # 以 server tagName 作为卷名前缀
            tagName = '%s-%s' % (get_server_name(svrId), diskType)
            nameTag = {"Key": "Name", "Value": tagName}
        # 否则从传入的body参数上获取
        else:
            volumeAz = parms.get('azName')
            nameTag = {"Key": "Name", "Value": parms.get('tagName')}
        tagSpecifications = [{"ResourceType": "volume", "Tags": [flagTag, nameTag]}]

        # 基于voluem type执行不同的创建参数
        if volumeType in ['gp3']:
            newVolume = client_ec2.create_volume(
                AvailabilityZone=volumeAz,
                Encrypted=parms['isEncrypted'],
                Size=parms['volumeSize'],
                VolumeType=parms['volumeType'],
                TagSpecifications=tagSpecifications,
                Iops=volumeIops,
                Throughput=volumeThruput,
            )
        elif volumeType in ['io1', 'io2']:
            newVolume = client_ec2.create_volume(
                AvailabilityZone=volumeAz,
                Encrypted=parms['isEncrypted'],
                Size=parms['volumeSize'],
                VolumeType=parms['volumeType'],
                TagSpecifications=tagSpecifications,
                Iops=volumeIops,
                MultiAttachEnabled=isMultiAttach,
            )
        else:  # ['gp2','sc1','st1','standard']
            newVolume = client_ec2.create_volume(
                AvailabilityZone=volumeAz,
                Encrypted=parms['isEncrypted'],
                Size=parms['volumeSize'],
                VolumeType=parms['volumeType'],
                TagSpecifications=tagSpecifications,
            )
        volItem = {
            'volumeId': newVolume['VolumeId'],
            'volumeState': newVolume['State'],
            'createTime': newVolume['CreateTime'],
            'volumeAz': newVolume['AvailabilityZone'],
        }

        # 如果传入了svrID和 attachPath参数，则将volume挂载到server上
        if svrId and attachPath:
            # wait until the volume is available
            waiter = client_ec2.get_waiter('volume_available')
            waiter.wait(VolumeIds=[newVolume['VolumeId']])

            attachResp = thisSvr.attach_volume(
                Device=parms["attachPath"], VolumeId=newVolume['VolumeId']
            )
            # 返回增加 volume attachment相关信息
            volAttach = {
                # 获取 volume状态更新
                'volumeState': attachResp['State'],
                'volumeAttach': [
                    {
                        'attachSvrId': svrId,
                        'attachSvr': get_server_name(svrId),
                        'attachPath': attachPath,
                        'diskType': diskType,
                    }
                ],
            }
            volItem.update(volAttach)

        response = Result(detail=volItem, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=5001, http_status_code=400)
        response.err_resp()


@bp.delete('/volume')
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


@bp.put('/volume/attach')
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


@bp.put('/volume/detach')
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
