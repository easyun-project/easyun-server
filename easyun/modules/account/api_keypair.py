# -*- coding: utf-8 -*-
"""
  @module:  KeyPair Management API
  @desc:    
"""

from flask import send_file
from io import BytesIO
from easyun import db
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.models import KeyStore
from easyun.common.schemas import DcNameQuery
from easyun.common.dc_utils import query_dc_region
from easyun.providers import get_datacenter
from .schema import KeypairParms, KeypairOut, KeyPairDelIn
from . import bp


def _keypair_to_dict(kp, region=None):
    """KeyPairInfo dataclass → 前端格式 dict（附加 keyRegion）"""
    from dataclasses import asdict
    d = asdict(kp)
    d['keyRegion'] = region
    return d


@bp.get('/keypair')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(KeypairOut(many=True))
def list_keypair(parm):
    '''获取指定数据中心的keypair信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        keyList = [_keypair_to_dict(k, query_dc_region(dcName)) for k in dc.list_keypairs()]
        resp = Result(detail=keyList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=8021)
        return resp.err_resp()


@bp.get('/keypair/list')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(KeypairOut(many=True))
def list_keypair_brief(parm):
    '''获取指定数据中心的keypair列表[仅基础字段]'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        dcRegion = query_dc_region(dcName)
        briefList = [{'keyName': k.name, 'keyType': k.key_type, 'keyRegion': dcRegion} for k in dc.list_keypairs()]
        resp = Result(detail=briefList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=8022)
        return resp.err_resp()


@bp.get('/keypair/<key_name>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(KeypairOut)
def get_keypair(key_name, parm):
    '''获取指定的keypair信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        kp = dc.get_keypair(key_name)
        resp = Result(detail=_keypair_to_dict(kp, query_dc_region(dcName)), status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=8022)
        return resp.err_resp()


@bp.post('/keypair')
@bp.auth_required(auth_token)
@bp.input(KeypairParms, arg_name='parm')
@bp.output(KeypairOut)
def add_keypair(parm):
    '''为指定数据中心添加keypair'''
    dcName = parm['dcName']
    keyName = parm['keyName']
    keyType = parm.get('keyType', 'rsa')
    try:
        dc = get_datacenter(dcName)
        kp_info, key_material = dc.create_keypair(keyName, keyType)
        storeItem = KeyStore(name=keyName, dc_name=dcName, material=key_material)
        db.session.add(storeItem)
        db.session.commit()
        resp = Result(detail=_keypair_to_dict(kp_info, query_dc_region(dcName)), status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=8010)
        return resp.err_resp()


@bp.delete('/keypair')
@bp.auth_required(auth_token)
@bp.input(KeyPairDelIn, arg_name='parm')
@bp.output(KeypairOut)
def del_keypair(parm):
    '''从指定数据中心删除keypair'''
    dcName = parm['dcName']
    keyName = parm['keyName']
    try:
        dc = get_datacenter(dcName)
        dc.delete_keypair(keyName)
    except Exception as ex:
        resp = Result(message=str(ex), status_code=8011)
        return resp.err_resp()
    try:
        storeItem = KeyStore.query.filter_by(name=keyName).first()
        if storeItem:
            db.session.delete(storeItem)
            db.session.commit()
        resp = Result(detail={'keyName': keyName}, message=f'Deleted:{keyName}', status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(detail={'keyName': keyName}, message=str(ex), status_code=8012)
        return resp.make_resp()


@bp.get('/keypair/store/<key_name>')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
def get_keystore(key_name, parm):
    '''获取指定的 keypair 文件下载'''
    try:
        storeItem = KeyStore.query.filter_by(name=key_name, dc_name=parm['dc']).first()
        keyMaterial = BytesIO(bytes(storeItem.get_material(), encoding='utf-8'))
        return send_file(keyMaterial, as_attachment=True, download_name=f"{storeItem.name}.{storeItem.format}")
    except Exception as ex:
        return str(ex)
