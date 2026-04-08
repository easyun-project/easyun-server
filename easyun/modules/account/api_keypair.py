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
from easyun.common.schemas import get_dc_name
from easyun.common.dc_utils import query_dc_region
from easyun.cloud import get_account
from .schema import KeypairParms, KeypairOut, KeyPairDelIn
from . import bp


@bp.get('/keypair')
@bp.auth_required(auth_token)
@bp.output(KeypairOut(many=True))
def list_keypair():
    '''获取指定数据中心的keypair信息'''
    dcName = get_dc_name()
    dcRegion = query_dc_region(dcName)
    try:
        account = get_account()
        keyList = account.list_keypairs(region=dcRegion, dc_name=dcName)
        resp = Result(detail=keyList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=8021)
        return resp.err_resp()


@bp.get('/keypair/list')
@bp.auth_required(auth_token)
@bp.output(KeypairOut(many=True))
def list_keypair_brief():
    '''获取指定数据中心的keypair列表[仅基础字段]'''
    dcName = get_dc_name()
    dcRegion = query_dc_region(dcName)
    try:
        account = get_account()
        keyList = account.list_keypairs(region=dcRegion, dc_name=dcName)
        resp = Result(detail=keyList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=8022)
        return resp.err_resp()


@bp.get('/keypair/<key_name>')
@bp.auth_required(auth_token)
@bp.output(KeypairOut)
def get_keypair(key_name):
    '''获取指定的keypair信息'''
    dcRegion = query_dc_region(get_dc_name())
    try:
        account = get_account()
        kp = account.get_keypair(key_name, region=dcRegion)
        resp = Result(detail=kp, status_code=200)
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
    dcName = get_dc_name()
    keyName = parm['keyName']
    keyType = parm.get('keyType', 'rsa')
    dcRegion = query_dc_region(dcName)
    try:
        account = get_account()
        kp_info, key_material = account.create_keypair(keyName, keyType, region=dcRegion, dc_name=dcName)
        storeItem = KeyStore(name=keyName, dc_name=dcName, material=key_material)
        db.session.add(storeItem)
        db.session.commit()
        resp = Result(detail=kp_info, status_code=200)
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
    dcName = get_dc_name()
    keyName = parm['keyName']
    dcRegion = query_dc_region(dcName)
    try:
        account = get_account()
        account.delete_keypair(keyName, region=dcRegion)
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
def get_keystore(key_name):
    '''获取指定的 keypair 文件下载'''
    try:
        storeItem = KeyStore.query.filter_by(name=key_name, dc_name=get_dc_name()).first()
        keyMaterial = BytesIO(bytes(storeItem.get_material(), encoding='utf-8'))
        return send_file(keyMaterial, as_attachment=True, download_name=f"{storeItem.name}.{storeItem.format}")
    except Exception as ex:
        return str(ex)
