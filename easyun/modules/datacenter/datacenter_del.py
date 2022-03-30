# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Module
  @desc:    Datacenter Delete API
  @auth:    aleck
"""

import boto3
import os, time
from flask import jsonify,current_app
from apiflask import APIBlueprint, Schema, input, output, auth_required
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from easyun import db
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.result import Result
from easyun.cloud.utils import gen_dc_tag, set_boto3_region
from .schemas import VpcListOut,DataCenterListIn
from . import bp, logger



@bp.delete('')
@auth_required(auth_token)
@input(DataCenterListIn)
def delete_datacenter(param):
    '''删除Datacenter'''
    dcName=param.get('dcName')
    flagTag = gen_dc_tag(dcName)

   # step 1: 判断是否为空
   # server, volume, rds, natgw


   # step 5: Update Datacenter metadata
    try:
        curr_account:Account = Account.query.first()
        curr_user = auth_token.current_user.username
        # curr_user = 'test-user'
        thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
        db.session.delete(thisDC)
        db.session.commit()

        stage = f"[DataCenter]' {thisDC.name} metadata updated."
        logger.info(stage)

    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2181)
        resp.err_resp()

    # step 6: Update Datacenter name list to DynamoDB
    try:
        # 待補充

        stage = f"[DataCenter]' {thisDC.name} deleted successfully !"
        logger.info(stage)

        resp = Result(
            detail = {
              'dcName' : thisDC.name, 
              'vpcID': thisDC.get_vpc()
            },
            status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(detail=str(ex) , status_code=2182)
        resp.err_resp()
  