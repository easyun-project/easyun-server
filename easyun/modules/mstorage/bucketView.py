from io import BytesIO
from typing import List
import boto3
from datetime import date, timedelta
from flask import send_file
from flask.views import MethodView, Schema
from apiflask import Schema
from apiflask.validators import Length
from marshmallow.fields import String
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from .s3_schema import newBucket, deleteBucket, vaildateBucket
from . import TYPE, bp, FLAG


def get_bucket_Region(bucketId):
    client = boto3.client('s3')
    response = client.get_bucket_location(
        Bucket = bucketId
    )
    if response['LocationConstraint'] == None:
        region = 'us-east-1'
    else:
        region = response['LocationConstraint']
    return region

@bp.route("/object/bucket")
class S3_Buckets(MethodView):
    # token 验证
    decorators = [auth_required(auth_token)]

    # 获取 Easyun Bucket 列表
    def get(self):
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
                    client = boto3.client('s3')
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
    
    # 添加存储桶
    @bp.input(newBucket, arg_name='data')
    def post(self,data):
        try:
            # 获取桶名
            # bucketId = newBucket['bucketId']
            bucketId = data.get('bucketId')
            # 获取是否开启版本控制（Enabled | Suspended）
            # versioningConfiguration = newBucket['versioningConfiguration']
            versioningConfiguration = data.get('versioningConfiguration')

            # 获取是否进行加密（true | false）
            # bucketEncryption = newBucket['bucketEncryption']
            bucketEncryption = data.get('bucketEncryption')
        
            if bucketEncryption == 'true':
                isEncryption = True
            elif bucketEncryption == 'false':
                isEncryption = False
            
            # 设定新增 Bucket 的 tag
            Tag = [{'Key':'Flag','Value':FLAG}]
            # 使用cloudcontrol api 需要定义DesiredState
            desiredState = {
                'bucketId' : bucketId,
                'VersioningConfiguration' : {'Status': versioningConfiguration },
                'BucketEncryption' : {"ServerSideEncryptionConfiguration":[{'BucketKeyEnabled' : isEncryption ,'ServerSideEncryptionByDefault' : {'SSEAlgorithm' : 'AES256'}}]},
                'Tags' : Tag,
                'PublicAccessBlockConfiguration' : {'BlockPublicAcls': False, 'BlockPublicPolicy' : False, 'IgnorePublicAcls' : False, 'RestrictPublicBuckets' : False}
            }
            region = data.get('region')
            CLIENT = boto3.client('cloudcontrol', region_name=region)
            # 通过boto3发起请求
            bucket = CLIENT.create_resource(
                TypeName = TYPE,
                DesiredState = str(desiredState)
            )
            
            response = Result(
                detail=[{
                    'bucketId' : bucket['ProgressEvent']['Identifier']
                }],
                status_code=4001
            )
            return response.make_resp()
            
        except Exception:
            response = Result(
                message='bucket create failed', status_code=4001,http_status_code=400
            )
            return response.err_resp()

# @bp.route("/object/bucket")
# class S3_Controller(MethodView):
#     # token 验证
#     decorators = [auth_required(auth_token)]