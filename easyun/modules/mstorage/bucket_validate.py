import boto3
import json
from apiflask import Schema, input, output, auth_required
from apiflask.schemas import EmptySchema 
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from flask import jsonify
from marshmallow import schema
from werkzeug.wrappers import response
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from . import TYPE, bp

s3 = boto3.resource('s3')
class Bucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )

# 验证bucket
@bp.post('/vaildate_bucket')
@auth_required(auth_token)
@input(Bucket)
def vaildate_bucket(Bucket):
    bucket = s3.Bucket(Bucket['bucketName'])
    detail = ''
    try:
        if bucket.creation_date == None:
            detail = 'Bucket does not exist'
        else:
            detail = 'Bucket already exists'
        response = Result(
            detail=[{
                'result' : detail
            }],
            status_code=4004
        )
        return response.make_resp()
    except Exception:
        response = Result(
            message='Get bucket message failed', status_code=4004,http_status_code=400
        )
        return response.err_resp()