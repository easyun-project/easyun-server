# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Module
  @desc:    Datacenter Delete API
  @auth:    aleck
"""


import imp
import boto3
import os, time
import json
from apiflask import APIBlueprint, Schema, input, output, abort, auth_required
from apiflask.fields import Integer, String
from apiflask.validators import Length, OneOf
from flask import jsonify,current_app
from datetime import date, datetime
from easyun import FLAG
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.result import Result, make_resp, error_resp, bad_request
from easyun.common.utils import gen_dc_tag, set_boto3_region
from easyun import db

from . import bp, DC_REGION, VERBOSE,TagEasyun
from .datacenter_sdk import datacentersdk

# from . import vpc_act
from .schemas import VpcListOut,DataCenterListIn


@bp.delete('')
#@auth_required(auth_token)
@input(DataCenterListIn)
def remove_datacenter(param):
    '''删除Datacenter'''

    dcName=param.get('dcName')
    flagTag = gen_dc_tag(dcName)

    pass

  