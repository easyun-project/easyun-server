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


@bp.get('/keypair')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(KeypairOut(many=True))
def list_keypair(parm):
    '''获取指定数据中心的keypair信息'''
    dcName = parm['dc']
    try:
        dc = get_datacenter(dcName)
        keyList = dc.list_keypairs()
        for k in keyList:
            k['keyRegion'] = query_dc_region(dcName)
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
        keyList = dc.list_keypairs()
        dcRegion = query_dc_region(dcName)
        briefList = [{'keyName': k['keyName'], 'keyType': k['keyType'], 'keyRegion': dcRegion} for k in keyList]
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
        keyItem = dc.get_keypair(key_name)
        keyItem['keyRegion'] = query_dc_region(dcName)
        resp = Result(detail=keyItem, status_code=200)
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
        result = dc.create_keypair(keyName, keyType)
        # 将 key material 存入数据库
        storeItem = KeyStore(name=keyName, dc_name=dcName, material=result['keyMaterial'])
        db.session.add(storeItem)
        db.session.commit()
        result['keyRegion'] = query_dc_region(dcName)
        del result['keyMaterial']
        resp = Result(detail=result, status_code=200)
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
    dcName = parm['dc']
    try:
        storeItem = KeyStore.query.filter_by(name=key_name, dc_name=dcName).first()
        keyMaterial = BytesIO(bytes(storeItem.get_material(), encoding='utf-8'))
        return send_file(keyMaterial, as_attachment=True, download_name=f"{storeItem.name}.{storeItem.format}")
    except Exception as ex:
        return str(ex)
