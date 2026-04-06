# -*- coding: utf-8 -*-
"""
  @module:  Server Management - parameters
  @desc:    Get parameters to create new server, like: AMI id, instance type
"""
from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length, OneOf
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.providers import get_datacenter
from .schemas import ImageItem, InsFamilyItem, InsTypeItem, InsTypeBriefItem
from . import bp


class ImageQuery(Schema):
    dc = String(required=True, validate=Length(0, 60), metadata={"example": 'Easyun'})
    arch = String(required=True, validate=OneOf(['x86_64', 'arm64']), metadata={"example": "x86_64"})
    os = String(required=True, validate=OneOf(['windows', 'linux']), metadata={"example": "linux"})


@bp.get('/param/image')
@bp.auth_required(auth_token)
@bp.input(ImageQuery, location='query')
@bp.output(ImageItem(many=True))
def list_images(parms):
    '''获取可用的AMI列表(包含 System Disk信息)'''
    try:
        dc = get_datacenter(parms['dc'])
        imgList = dc.list_images(arch=parms['arch'], os_type=parms['os'])
        resp = Result(detail=imgList, message=f"{len(imgList)},success", status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3010)
        return response.err_resp()


@bp.get('/param/instype/family')
@bp.auth_required(auth_token)
@bp.input({'dc': String(required=True)}, location='query', arg_name='parm')
@bp.output(InsFamilyItem(many=True))
def list_ins_family(parm):
    '''获取可用的Instance Family列表'''
    dc = get_datacenter(parm['dc'])
    resp = Result(detail=dc.list_instance_families(), status_code=200)
    return resp.make_resp()


class InsTypelsQuery(Schema):
    dc = String(required=True, validate=Length(0, 60), metadata={"example": 'Easyun'})
    arch = String(required=True, validate=OneOf(['x86_64', 'arm64']), metadata={"example": "x86_64"})
    family = String(required=True, metadata={"example": "m5"})


@bp.get('/param/instype/list')
@bp.auth_required(auth_token)
@bp.input(InsTypelsQuery, location='query', arg_name='parm')
@bp.output(InsTypeBriefItem(many=True))
def get_ins_type_list(parm):
    '''获取可用的Instance Types列表(不含成本)'''
    try:
        dc = get_datacenter(parm['dc'])
        instypeList = dc.list_instance_types(arch=parm['arch'], family=parm['family'])
        briefList = [{'insType': t['insType'], 'familyName': t['familyName'], 'familyDes': t.get('familyDes', '')} for t in instypeList]
        resp = Result(detail=briefList, message=f"{len(briefList)},success", status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3020)
        return response.err_resp()


class InsTypeQuery(Schema):
    dc = String(required=True, validate=Length(0, 60), metadata={"example": 'Easyun'})
    arch = String(required=True, validate=OneOf(['x86_64', 'arm64']), metadata={"example": "x86_64"})
    family = String(required=True, metadata={"example": "m5"})
    os = String(required=False, metadata={"example": "linux"})


@bp.get('/param/instype')
@bp.auth_required(auth_token)
@bp.input(InsTypeQuery, location='query', arg_name='parm')
@bp.output(InsTypeItem(many=True))
def list_ins_types(parm):
    '''获取可用的Instance Types列表(含月度成本)'''
    try:
        dc = get_datacenter(parm['dc'])
        instypeList = dc.list_instance_types(arch=parm['arch'], family=parm['family'])
        for t in instypeList:
            t['monthPrice'] = dc.get_instance_pricing(t['insType'], parm.get('os'))
        resp = Result(detail=instypeList, message=f"{len(instypeList)},success", status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=3020)
        return response.err_resp()
