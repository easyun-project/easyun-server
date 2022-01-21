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
from . import bp

class deleteBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )

# 删除bucket
@bp.delete('/bucket')
@auth_required(auth_token)
@input(deleteBucket)
def delete_bucket(deleteBucket):
    bucketName = deleteBucket['bucketName']
    CLIENT = boto3.client('s3')
    try:
        result = CLIENT.delete_bucket(
            Bucket = bucketName
        )
        response = Result(
            detail=[{
                'message' : 'bucket delete succee'
            }],
            status_code=4003
        )
        return response.make_resp()
    except Exception:
        response = Result(
            message='bucket delete failed', status_code=4003,http_status_code=400
        )
        return response.err_resp()