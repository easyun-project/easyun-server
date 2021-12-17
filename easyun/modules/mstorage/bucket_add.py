import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.schemas import EmptySchema 
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from flask import jsonify
from werkzeug.wrappers import response
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from . import TYPE, bp, FLAG

Tag = [{'Key':'FLAG','Value':FLAG}]
class newBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )
    versioningConfiguration = String(required=True)
    bucketEncryption = String(required=True)
    region = String(required=True)
    
# 新增bucket
@bp.post('/add_bucket')
#@auth_required(auth_token)
@input(newBucket)
def add_bucket(newBucket):
    print(newBucket)
    try:
        # 获取桶名
        bucketName = newBucket['bucketName']
        # 获取是否开启版本控制（Enabled | Suspended）
        versioningConfiguration = newBucket['versioningConfiguration']
        print(versioningConfiguration)
        print(type(versioningConfiguration))
        # 获取是否进行加密（true | false）
        bucketEncryption = newBucket['bucketEncryption']
    
        if bucketEncryption == 'true':
            isEncryption = True
        elif bucketEncryption == 'false':
            isEncryption = False
        print(type(isEncryption))
        # 使用cloudcontrol api 需要定义DesiredState
        desiredState = {
            'BucketName' : bucketName,
            'VersioningConfiguration' : {'Status': versioningConfiguration },
            'BucketEncryption' : {"ServerSideEncryptionConfiguration":[{'BucketKeyEnabled' : isEncryption ,'ServerSideEncryptionByDefault' : {'SSEAlgorithm' : 'AES256'}}]},
            'Tags' : Tag,
            'PublicAccessBlockConfiguration' : {'BlockPublicAcls': False, 'BlockPublicPolicy' : False, 'IgnorePublicAcls' : False, 'RestrictPublicBuckets' : False}
        }
        CLIENT = boto3.client('cloudcontrol', region_name=newBucket['region'])
        # 通过boto3发起请求
        bucket = CLIENT.create_resource(
            TypeName = TYPE,
            DesiredState = str(desiredState)
        )
        
        response = Result(
            detail=[{
                'bucketName' : bucket['ProgressEvent']['Identifier']
            }],
            status_code=4001
        )
        return response.make_resp()
        
    except Exception:
        response = Result(
            message='bucket creation failed', status_code=4001,http_status_code=400
        )
        return response.err_resp()