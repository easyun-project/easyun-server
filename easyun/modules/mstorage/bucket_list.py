import boto3
import json
from apiflask import Schema, input, output, auth_required
from apiflask.schemas import EmptySchema 
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length, OneOf
from flask import jsonify
from werkzeug.wrappers import response
from easyun.common.auth import auth_token
from easyun.common.result import Result, make_resp, error_resp, bad_request
from . import TYPE, bp

# bucket detail:
# bucketName
# bucketStatus
# bucketRegion
# 获取一个字典列表返回给端
client = boto3.client('s3')
def get_bucket_Region(bucketName):
    response = client.get_bucket_location(
        Bucket = bucketName
    )
    if response['LocationConstraint'] == None:
        region = 'us-east-1'
    else:
        region = response['LocationConstraint']
    return region

@bp.get('/list_bucket')
@auth_required(auth_token)
def listBucket():
    try:
        CLIENT = boto3.client('resourcegroupstaggingapi') 
        response = CLIENT.get_resources(TagFilters=[{'Key': 'Flag','Values':['Easyun']}],ResourceTypeFilters=['s3']) 
        buckets = response['ResourceTagMappingList']
        bucketsName = []
        for bucket in buckets:
            name = bucket['ResourceARN']
            bucketsName.append({'Name' : name[13:]})
        for bucket in bucketsName:
            name = bucket['Name']
            # 获取存储桶所在的region
            bucketRegion = get_bucket_Region(name)
            try:
                # 获取存储桶的权限
                access = client.get_public_access_block(Bucket=name)
                if access['PublicAccessBlockConfiguration']['BlockPublicPolicy'] == False or access['PublicAccessBlockConfiguration']['IgnorePublicAcls'] == False or access['PublicAccessBlockConfiguration']['BlockPublicPolicy'] == False or access['PublicAccessBlockConfiguration']['BlockPublicPolicy'] == False:
                    bucketStatus = 'Objects can be public'
                else:
                    bucketStatus = 'Bucket and objects not public'
            except Exception as e:
                if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                    # print('\t no Public Access')
                    bucketStatus = 'Objects can be public'
                else:
                    print("unexpected error: %s" % (e.response))
            bucketDetial = {'bucketStatus':bucketStatus,'bucketRegion':bucketRegion}
            bucket.update(bucketDetial)
        response = Result(
            detail=[{
                'bucketList' : bucketsName 
            }],
            status_code=4002
        )
        return response.make_resp()
    except Exception:
        response = Result(
            message='Get bucket list failed', status_code=4002, http_status_code=400
        )
        return response.err_resp()