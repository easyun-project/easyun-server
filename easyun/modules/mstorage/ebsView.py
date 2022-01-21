import boto3
from datetime import date, timedelta
from flask import send_file
from flask.views import MethodView
from apiflask import auth_required, Schema
from apiflask.decorators import output, input
from apiflask.validators import Length
from marshmallow.fields import String
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from .volume_schema import newVolume
from . import TYPE, bp, FLAG

@bp.route("/EBS/Volume")
class EBS_Volume(MethodView):
    # token 验证
    decorators = [auth_required(auth_token)]

    # 创建EBS卷
    @input(newVolume)
    def post(self, data):
        try:
            ec2Client = boto3.client('ec2')
            
            # 获取可用区信息
            az = data.get('az')
            # 创建EBS卷
            volumeEncryption = data.get('encryption')
            if volumeEncryption == 'true':
                isEncryption = True
            elif volumeEncryption == 'false':
                isEncryption = False
           
            createResult = ec2Client.create_volume(
                AvailabilityZone = az,
                Encrypted = isEncryption,
                Size = int(data.get('size')),
                VolumeType = data.get('diskType'),
                Iops = int(data.get('iops')),
                Throughput = int(data.get('thruput')),
                TagSpecifications = [{
                    'ResourceType' : 'volume',
                    'Tags' : [{ 'Key':'Flag','Value':FLAG }]
                }]
            )
            volumeId = createResult['VolumeId']
            
            response = Result(
                detail=[{
                    'VolumeId' : volumeId
                }],
                status_code=5001
            )
            return response.make_resp()
        except Exception:
            response = Result(
                message='volume attach failed', status_code=5001,http_status_code=400
            )
            return response.err_resp()