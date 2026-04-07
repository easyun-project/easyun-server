# -*- coding: utf-8 -*-
"""
  @module:  Server Detail
  @desc:    Get Server detail info, manage disk/eip/secgroup/tags
"""

from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery, get_dc_name, TagItem
from easyun.providers import get_datacenter
from .schemas import SvrEntityOut, SvrInstypeParam, MsgOut
from . import bp


# --- Schemas ---

class DiskInfoIn(Schema):
    action = String(required=True, metadata={"example": 'attach'})
    svrId = String(required=True, metadata={"example": 'i-0d05b7bda069b8c1d'})
    diskPath = String(required=True, metadata={"example": '/dev/sdf'})
    volumeId = String(required=True, metadata={"example": 'vol-0fcb3e28f8687f74d'})


class EipAttachInfoIn(Schema):
    action = String(required=True, validate=OneOf(['attach', 'detach']), metadata={"example": 'attach'})
    svrId = String(required=True, metadata={"example": 'i-0d05b7bda069b8c1d'})
    publicIp = String(required=True, metadata={"example": '34.192.222.116'})


class SgAttachInfoIn(Schema):
    action = String(required=True, validate=OneOf(['attach', 'detach']), metadata={"example": 'attach'})
    svrId = String(required=True, metadata={"example": 'i-0d05b7bda069b8c1d'})
    secgroupId = String(required=True, metadata={"example": 'sg-0bb69bb599b303a1e'})


def _full_detail_to_response(d):
    """ServerFullDetail dataclass → 前端嵌套结构"""
    return {
        'svrProperty': {
            'instanceName': d.name, 'instanceType': d.instance_type,
            'vCpu': d.vcpu, 'memory': d.memory_gib,
            'privateIp': d.private_ip, 'publicIp': d.public_ip, 'isEip': d.is_eip,
            'status': d.state, 'instanceId': d.id, 'launchTime': d.launch_time,
            'privateIpv4Dns': d.private_dns, 'publicIpv4Dns': d.public_dns,
            'platformDetails': d.platform, 'virtualization': d.virtualization,
            'tenancy': d.tenancy, 'usageOperation': d.usage_operation,
            'monitoring': d.monitoring, 'terminationProtection': d.termination_protection,
            'amiId': d.ami_id, 'amiName': d.ami_name, 'amiPath': d.ami_path,
            'keyPairName': d.key_pair_name, 'iamRole': d.iam_role,
        },
        'svrConfig': {'arch': d.arch, 'os': d.os_code},
        'svrDisk': {'volumeIds': d.volume_ids},
        'svrNetworking': {'privateIp': d.private_ip, 'publicIp': d.public_ip},
        'svrSecurity': d.security_groups,
        'svrTags': d.tags,
        'svrConnect': {'userName': 'ec2-user', 'publicIp': d.public_ip},
    }


# --- Endpoints ---

@bp.get('/detail/<svr_id>')
@bp.auth_required(auth_token)
@bp.output(SvrEntityOut)
def get_server_detail(svr_id):
    '''获取指定云服务器详情信息'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(svr_id)
        detail = _full_detail_to_response(svr.get_detail())
        res = Result(detail, status_code=200)
        return res.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3001, http_status_code=400)
        response.err_resp()


@bp.get('/instype/<svr_id>')
@bp.auth_required(auth_token)
@bp.output(SvrInstypeParam)
def get_ins_types(svr_id):
    '''获取指定云服务器实例参数'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(svr_id)
        resp = Result(detail=svr.get_instype_param(), status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3001, http_status_code=400)
        response.err_resp()


@bp.put('/disk')
@bp.auth_required(auth_token)
@bp.input(DiskInfoIn, arg_name='param')
@bp.output(MsgOut)
def attach_disk(param):
    '''云服务器关联与解绑磁盘(volume)'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(param['svrId'])
        if param['action'] == 'attach':
            svr.attach_disk(param['volumeId'], param['diskPath'])
        elif param['action'] == 'detach':
            svr.detach_disk(param['volumeId'], param['diskPath'])
        else:
            raise ValueError('invalid action')
        response = Result(detail={'msg': f"{param['action']} disk success"}, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3001, http_status_code=400)
        response.err_resp()


@bp.put('/eip')
@bp.auth_required(auth_token)
@bp.input(EipAttachInfoIn, arg_name='param')
@bp.output(MsgOut)
def attach_eip(param):
    '''云服务器关联和解绑静态IP(eip)'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(param['svrId'])
        if param['action'] == 'attach':
            svr.attach_eip(param['publicIp'])
        elif param['action'] == 'detach':
            svr.detach_eip(param['publicIp'])
        else:
            raise ValueError('invalid action')
        response = Result(detail={'msg': f"{param['action']} eip success"}, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3001, http_status_code=400)
        response.err_resp()


@bp.put('/secgroup')
@bp.auth_required(auth_token)
@bp.input(SgAttachInfoIn, arg_name='param')
@bp.output(MsgOut)
def attach_secgroup(param):
    '''云服务器关联和解绑安全组(secgroup)'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(param['svrId'])
        if param['action'] == 'attach':
            svr.attach_secgroup(param['secgroupId'])
        elif param['action'] == 'detach':
            svr.detach_secgroup(param['secgroupId'])
        else:
            raise ValueError('invalid action')
        response = Result(detail={'msg': f"{param['action']} secgroup success"}, status_code=200)
        return response.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3001, http_status_code=400)
        response.err_resp()


@bp.get('/tags/<svr_id>')
@bp.auth_required(auth_token)
@bp.output(TagItem(many=True))
def list_svr_tags(svr_id):
    '''获取指定云服务器的用户Tags'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(svr_id)
        response = Result(detail=svr.get_tags(), status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3031)
        response.err_resp()


@bp.put('/tags/<svr_id>')
@bp.auth_required(auth_token)
@bp.input(TagItem, arg_name='tag')
@bp.output(TagItem(many=True))
def mod_svr_tags(svr_id, parm, tag):
    '''为指定云服务器新增/修改用户Tags'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(svr_id)
        userTags = svr.add_tag(tag)
        response = Result(detail=userTags, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3032, http_status_code=400)
        response.err_resp()


@bp.delete('/tags/<svr_id>')
@bp.auth_required(auth_token)
@bp.input(TagItem, arg_name='tag')
@bp.output(TagItem(many=True))
def del_svr_tags(svr_id, parm, tag):
    '''为指定云服务器删除用户Tags'''
    try:
        dc = get_datacenter(get_dc_name())
        svr = dc.get_server(svr_id)
        userTags = svr.remove_tag(tag)
        response = Result(detail=userTags, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3033, http_status_code=400)
        response.err_resp()
