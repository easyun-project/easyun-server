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
from easyun.common.schemas import DcNameQuery, TagItem
from easyun.providers import get_datacenter
from .schemas import SvrEntityOut, SvrInstypeParam, MsgOut
from . import bp


# --- Schemas ---

class DiskInfoIn(Schema):
    action = String(required=True, metadata={"example": 'attach'})
    svrId = String(required=True, metadata={"example": 'i-0d05b7bda069b8c1d'})
    diskPath = String(required=True, metadata={"example": '/dev/sdf'})
    volumeId = String(required=True, metadata={"example": 'vol-0fcb3e28f8687f74d'})
    dcName = String(metadata={"example": "Easyun"})


class EipAttachInfoIn(Schema):
    action = String(required=True, validate=OneOf(['attach', 'detach']), metadata={"example": 'attach'})
    svrId = String(required=True, metadata={"example": 'i-0d05b7bda069b8c1d'})
    publicIp = String(required=True, metadata={"example": '34.192.222.116'})
    dcName = String(metadata={"example": "Easyun"})


class SgAttachInfoIn(Schema):
    action = String(required=True, validate=OneOf(['attach', 'detach']), metadata={"example": 'attach'})
    svrId = String(required=True, metadata={"example": 'i-0d05b7bda069b8c1d'})
    secgroupId = String(required=True, metadata={"example": 'sg-0bb69bb599b303a1e'})
    dcName = String(metadata={"example": "Easyun"})


# --- Endpoints ---

@bp.get('/detail/<svr_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(SvrEntityOut)
def get_server_detail(svr_id, parm):
    '''获取指定云服务器详情信息'''
    try:
        dc = get_datacenter(parm['dc'])
        svr = dc.get_server(svr_id)
        detail = svr.get_detail()
        res = Result(detail, status_code=200)
        return res.make_resp()
    except Exception as e:
        response = Result(message=str(e), status_code=3001, http_status_code=400)
        response.err_resp()


@bp.get('/instype/<svr_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(SvrInstypeParam)
def get_ins_types(svr_id, parm):
    '''获取指定云服务器实例参数'''
    try:
        dc = get_datacenter(parm['dc'])
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
        dc = get_datacenter(param.get('dcName', 'Easyun'))
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
        dc = get_datacenter(param.get('dcName', 'Easyun'))
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
        dc = get_datacenter(param.get('dcName', 'Easyun'))
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
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(TagItem(many=True))
def list_svr_tags(svr_id, parm):
    '''获取指定云服务器的用户Tags'''
    try:
        dc = get_datacenter(parm['dc'])
        svr = dc.get_server(svr_id)
        response = Result(detail=svr.get_tags(), status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3031)
        response.err_resp()


@bp.put('/tags/<svr_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.input(TagItem, arg_name='tag')
@bp.output(TagItem(many=True))
def mod_svr_tags(svr_id, parm, tag):
    '''为指定云服务器新增/修改用户Tags'''
    try:
        dc = get_datacenter(parm['dc'])
        svr = dc.get_server(svr_id)
        userTags = svr.add_tag(tag)
        response = Result(detail=userTags, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3032, http_status_code=400)
        response.err_resp()


@bp.delete('/tags/<svr_id>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.input(TagItem, arg_name='tag')
@bp.output(TagItem(many=True))
def del_svr_tags(svr_id, parm, tag):
    '''为指定云服务器删除用户Tags'''
    try:
        dc = get_datacenter(parm['dc'])
        svr = dc.get_server(svr_id)
        userTags = svr.remove_tag(tag)
        response = Result(detail=userTags, status_code=200)
        return response.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3033, http_status_code=400)
        response.err_resp()
