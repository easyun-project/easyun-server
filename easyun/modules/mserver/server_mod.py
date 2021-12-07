# -*- coding: utf-8 -*-
'''
@Description: Server Management - Modify: Name, Instance type, 
@LastEditors: 
'''
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from flask import jsonify
from werkzeug.wrappers import response
from easyun.common.auth import auth_token
from easyun.common.result import make_resp, error_resp, bad_request
from . import bp, REGION, FLAG



@bp.post('/modify')
@auth_required(auth_token)
# @input()
# @output()
def update_svr(operate):
    pass
