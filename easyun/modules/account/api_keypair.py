# -*- coding: utf-8 -*-
"""dashboard model views."""

import boto3
from botocore.exceptions import ClientError
from apiflask import auth_required, Schema, output, input
from flask import send_file
from io import BytesIO
from easyun import db
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.models import Account, KeyStore
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import set_boto3_region, gen_dc_tag, query_dc_region
from .schema import KeypairParms, KeypairOut, KeyPairDelIn
from . import bp


@bp.get('/keypair')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(KeypairOut(many=True))
# @log.api_error(logger)
def list_keypair(parm):
    '''获取指定数据中心的keypair信息'''
    dcName=parm['dc']
    try:
        dcRegion = set_boto3_region(dcName)
        client_ec2 = boto3.client('ec2')
        filterTag = gen_dc_tag(dcName, 'filter')
        keys = client_ec2.describe_key_pairs(
            Filters=[ filterTag ],
        ).get('KeyPairs')
        keyList = []
        for key in keys:
            keyTags = [t for t in key.get('Tags') if t['Key'] != 'Flag']
            #生成 keypair下载链接
            # keyFile = gen_key_file(key['KeyName'])
            keyItem = {
                'keyName':key['KeyName'],
                'keyType':key['KeyType'],
                'keyFingerprint' : key['KeyFingerprint'],
                'keyTags' : keyTags,
                # 'keyFile' : keyFile,
                'keyRegion' : dcRegion
            }
            keyList.append(keyItem)

        resp = Result(
            detail = keyList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message = ex, 
            status_code=8021,
        )
        return resp.err_resp()



@bp.get('/keypair/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(KeypairOut(many=True))
# @log.api_error(logger)
def list_keypair_brief(parm):
    '''获取指定数据中心的keypair列表[仅基础字段]'''
    dcName=parm['dc']
    try:
        dcRegion = set_boto3_region(dcName)
        client_ec2 = boto3.client('ec2')
        filterTag = gen_dc_tag(dcName, 'filter')
        keys = client_ec2.describe_key_pairs(
            Filters=[filterTag],
        ).get('KeyPairs')
        keyList = []
        for key in keys:
            keyItem = {
                'keyName':key['KeyName'],
                'keyType':key['KeyType'],
                'keyRegion':dcRegion
            }
            keyList.append(keyItem)

        resp = Result(
            detail = keyList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message = ex, 
            status_code=8022
        )
        return resp.err_resp()



@bp.get('/keypair/<key_name>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
@bp.output(KeypairOut)
# @log.api_error(logger)
def get_keypair(key_name, parm):
    '''获取指定的keypair信息'''
    dcName=parm['dc']    
    try:
        dcRegion = query_dc_region(dcName)
        resource_ec2 = boto3.resource('ec2', region_name=dcRegion)
        # thisKeyinfo = resource_ec2.KeyPairInfo(key_name)
        # explain: https://github.com/boto/boto3/issues/1945#issuecomment-492803349
        thisKey = resource_ec2.KeyPair(key_name)        
        keyTags = [t for t in thisKey.tags if t['Key'] != 'Flag']
        #生成 keypair下载链接
        # keyFile = gen_key_file(key_name)
        keyItem = {
            'keyName':key_name,
            'keyType': thisKey.key_type,
            'keyFingerprint' : thisKey.key_fingerprint,
            'keyTags' : keyTags,
            # 'keyFile' : keyFile,
            'keyRegion' : dcRegion
        }
        resp = Result(
            detail = keyItem,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message = str(ex), 
            status_code=8022
        )
        return resp.err_resp()


@bp.post('/keypair')
@auth_required(auth_token)
@bp.input(KeypairParms)
@bp.output(KeypairOut)
# @log.api_error(logger)
def add_keypair(parm):
    '''为指定数据中心添加keypair'''
    dcName = parm['dcName']
    keyName = parm['keyName']
    if parm.get('keyType'):
        keyType = parm.get('keyType')  
    else: 
        keyType = 'rsa'
    try:
        #Step1: 在 datacenter对应region新建 keypair
        dcRegion = query_dc_region(dcName)
        resource_ec2 = boto3.resource('ec2', region_name=dcRegion)
        flagTag = gen_dc_tag(dcName)

        keyPair = resource_ec2.create_key_pair(
            KeyName = keyName,
            KeyType= keyType,
            TagSpecifications=[
                {
                    'ResourceType': 'key-pair',
                    'Tags': [ flagTag ]
                },
            ]
        )

        #Step2: 将 key material 存入数据库
        storeItem = KeyStore(
            name = keyName,
            dc_name = dcName,
            material = keyPair.key_material
        )
        db.session.add(storeItem)
        db.session.commit()

        #Step3: 生成 keypair 文件链接
        # keyFile = gen_key_file(keyName)

        resp = Result(
            detail = {
                'keyName':keyName,
                'keyType': keyType,
                'keyFingerprint' : keyPair.key_fingerprint,
                # 'keyFile' : keyFile,
                'keyRegion' : dcRegion

            },
            status_code=200
        )
        return resp.make_resp()

    # except ClientError as ce:
    except Exception as ex:
        resp = Result(
            message = str(ex), 
            status_code=8010
        )
        return resp.err_resp()



@bp.delete('/keypair')
@auth_required(auth_token)
@bp.input(KeyPairDelIn)
# @bp.output(SSHKeysOutputSchema(many=True))
# @log.api_error(logger)
def del_keypair(parm):
    '''从指定数据中心删除keypair'''
    dcName = parm['dcName']
    keyName = parm['keyName']
    #Step1: 将 keypair 从cloud删除    
    try:
        dcRegion = query_dc_region(dcName)
        client_ec2 = boto3.client('ec2', region_name=dcRegion)        
        client_ec2.delete_key_pair(KeyName=keyName)
    except Exception as ex:
        resp = Result(
            message = str(ex), 
            status_code=8011
        )
        return resp.err_resp()

    #Step2: 将 key material 从数据库删除
    try:    
        storeItem:KeyStore = KeyStore.query.filter_by(name = keyName).first()
        db.session.delete(storeItem)
        db.session.commit()

        resp = Result(
            detail = {
                'keyName':keyName,
            },
            message = 'Deleted:'+keyName,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            detail = {
                'keyName':keyName,
            },            
            message = str(ex), 
            status_code=8012
        )
        return resp.make_resp()


@bp.get('/keypair/store/<key_name>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
def get_keystore(key_name, parm):
    '''获取指定的 keypair 文件下载'''
    dcName = parm['dc']
    keyFile = send_keysotre(key_name, dcName)
    return keyFile


def send_keysotre(key_name, dc_name, format='pem'):
    '''生成 keypair 文件链接'''
    try:
        storeItem:KeyStore = KeyStore.query.filter_by(name = key_name, dc_name = dc_name).first()
        keyMaterial = BytesIO(bytes(storeItem.get_material(), encoding='utf-8'))
        if format == 'pem':            
            keyFile = send_file(
                keyMaterial,
                # mimetype='application/pem',
                #作为下载附件参数
                as_attachment=True,      
                attachment_filename=f"{storeItem.name}.{storeItem.format}"
            )
        elif format == 'ppk':
            # 转换为ppk格式后返回(TBD)
            pass
        return keyFile
    except Exception as ex:
        return str(ex)
