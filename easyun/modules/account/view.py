# -*- coding: utf-8 -*-
"""dashboard model views."""
import boto3
import os
from flask.views import MethodView
from apiflask import auth_required, Schema
from apiflask.decorators import output, input
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account
from .schema import SSHKeysOutputSchema, AWSInfoOutSchema, CreateSSHKeySchema
# 导入boto错误类型
from botocore.exceptions import ClientError


@auth_required(auth_token)
@bp.get("/aws_info")
@output(AWSInfoOutSchema)
def aws_info():
    try:
        account: Account = Account.query.first()
        res = Result(detail=account)
        return res.make_resp()
    except Exception as e:
        res = Result(message=str(e), status_code=2001, http_status_code=500)
        res.err_resp()


REGION = 'us-east-1'


@bp.route("/ssh-keys")
class SSHKeys(MethodView):

    # decorators = [auth_required(auth_token)]

    @output(SSHKeysOutputSchema(many=True))
    def get(self):
        result = Result()
        return result.make_resp()

    @input(CreateSSHKeySchema)
    @output(CreateSSHKeySchema)
    def post(self, data):
        try:
            keyname = data.get('key_name')
            client = boto3.client('ec2', region_name=REGION)

            resp = client.create_key_pair(KeyName=keyname)
            key_material = resp.get('KeyMaterial')
            key_name = resp.get('KeyName')
            # 保存生成文件
            path = os.path.join(os.getcwd(), 'keys')
            keypairfilename = keyname+'.pem'
            if os.path.exists(os.path.join(path)):
                with open(os.path.join('./keys/', keypairfilename), 'w', encoding='utf-8') as file:
                    file.write(key_material)

            result = Result(detail={
                "key_name": key_name
            })
            return result.make_resp()
        except ClientError as client_err:
            err_code = 8001
            if client_err.response.get('Error').get("Code") == 'InvalidKeyPair.Duplicate':
                err_code = 8010
            result = Result(message=client_err.response.get('Error').get('Message'),
                            status_code=err_code,
                            http_status_code=400)
            result.err_resp()
        except Exception as e:
            print(e, type(e))
            result = Result(http_status_code=500)
            result.err_resp()
        # result = Result()
        # return result.make_resp()

    # @output({})
    def delete(self):
        client = boto3.client('ec2', region_name=REGION)
        resp = client.delete_key_pair(KeyName='easyun-dev-key')
        result = Result(detail=resp)
        return result.make_resp()
