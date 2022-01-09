# -*- coding: utf-8 -*-
"""dashboard model views."""
from io import BytesIO
from typing import List
import boto3
from flask import send_file
from flask.views import MethodView
from apiflask import auth_required, Schema
from apiflask.decorators import output, input
from apiflask.validators import Length
from marshmallow.fields import String
from easyun.common.exception.model_errs import KeyPairsRepeat
from easyun.common.result import Result
from . import bp
from easyun import db
from easyun.common.auth import auth_token
from easyun.common.models import Account, KeyPairs
from .schema import FreeTierInputSchema, SSHKeysOutputSchema, AWSInfoOutSchema, CreateSSHKeySchema
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


@bp.route("/ssh_keys")
class SSHKeys(MethodView):

    decorators = [auth_required(auth_token)]

    @output(SSHKeysOutputSchema(many=True))
    def get(self):
        key_pairs:List[KeyPairs] = KeyPairs.query.all()
        result = Result(detail=key_pairs)
        return result.make_resp()

    @input(CreateSSHKeySchema)
    @output(SSHKeysOutputSchema)
    def post(self, data):
        try:
            keyname = data.get('key_name')
            # 写数据库
            key_pair = KeyPairs.New(name=keyname, region=REGION)
            client = boto3.client('ec2', region_name=REGION)
            resp = client.create_key_pair(KeyName=keyname)
            key_pair_args = {
                "region": REGION,
                "name": resp.get('KeyName'),
                "material": resp.get('KeyMaterial'),
                "extension": 'pem'
            }
            # update database
            key_pair.update(**key_pair_args)
            db.session.add(key_pair)
            db.session.commit()
            result = Result(detail=key_pair)
            return result.make_resp()
        except ClientError as client_err:
            err_code = 8001
            if client_err.response.get('Error').get("Code") == 'InvalidKeyPair.Duplicate':
                err_code = 8010
            result = Result(message=client_err.response.get('Error').get('Message'),
                            status_code=err_code,
                            http_status_code=400)
            result.err_resp()
        except KeyPairsRepeat as key_repeat:
            result = Result(message=key_repeat.err_msg, status_code=8010, http_status_code=400)
            result.err_resp()
        except Exception as e:
            print(e, type(e))
            result = Result(http_status_code=500)
            result.err_resp()


@bp.route("/ssh_keys/<int:id>")
class KeyPairsController(MethodView):
    
    decorators = [auth_required(auth_token)]

    def get(self, id:int):
        key_pair_obj: KeyPairs = KeyPairs.query.get(id)
        if key_pair_obj is None:
            return "404"
        return send_file(BytesIO(bytes(key_pair_obj.material, encoding='utf-8')),
                        download_name=f"{key_pair_obj.name}.{key_pair_obj.extension}",
                        as_attachment=True)

    def delete(self, id:int):
        try:
            key_pair:KeyPairs = KeyPairs.query.get(id)
            client = boto3.client('ec2', region_name=key_pair.region)
            resp = client.delete_key_pair(KeyName=key_pair.name)

            db.session.delete(key_pair)
            db.session.commit()
            result = Result(detail=resp)
            return result.make_resp()
        except Exception as e:
            print(e, type(e))
            pass


# @bp.post('/dev')
# @input({"key": String(), "value": String(validate=Length(0, 2048))})
# def dev(data):
#     # -----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEArNMFwG5XmxGwwkENbHfqY6RTOOuab/KQ6HA7gjJXKdDkq3wx\nglWi7P0WZy9Veu0NMpKOIT6oUXiAVTsXrDwbZHdGFmfLixWhtX1NGMlj8iYctBDA\nuhEbTAJfM1vsS9ubLeVp8Y+qkCYAEojbmo++ibBw1fRGBgLMs5z3y68l1nMHSOoJ\ndLXokff1f1JmDm2H3sOtcXuzdnXZC83RyQxg6Ev9nPB53pmr4ydUQKH+cnL7wZiU\n6fKXpSDHzS3RElFsA0hk2lzTLh0ukdGuQEDivG5gwkqgCHS2ol7rECmnJc5+MBwG\nCyZcigbL578rSXqzW7f9Sm6LNUN0qQWD1hz/kwIDAQABAoIBAQCGU3Yy/RCGbJeQ\nRHOkjQfW7o/ou+bLgCN1JlZ6eZoZ3Ez/pIXuoZUC0iupg7bS1pDdb9+co1C8Egbd\nOBLMQeOgkLwfCgnATs3jfEKCM3XFbi39HtBNTqKCz40jJB1jUIsqfxd7M4kEhSSl\nQ048seEMr+DjyvrqDR8Bs809uSKVrIaZbSoE4dDd8gXmbHKyycJHFI2J0c0kyxFG\n3jy1EpggthFK54P46zK1W0Ap2JxBJ4mBnR5jzkWY/pzK/7yjjG6fYZLzLBtKK7L6\nOHTzph5c3wVSgWjLKMORobXv6WMrOq2PPXlgdQd+j+Vm4yEbzHo0nQSC3XL9GNUj\n2dk3UaiRAoGBAODBt5yK0ltTAytw2X7qkNqcHpZG0wVe7Mt8EsFbpb6W71ip/1zt\nM5/z5qQoHHcm85tos4NaV1kLCLEdqMah0r/GJEOfkjB2fmERDPZlXQ/z+1ieAOcV\ne8ARZ99tVQUvqeA2mT2tHBfVrHSDEORcfFvp6DU/F0eh9lRXbBBa9ExNAoGBAMTZ\nN8aNVgnx+lQSDxNj7XUUIfn5s6Ga5YF3AbKe6vSFnkpM3jOv6u2v4OuTHXSXIrqd\nB8QhTwcKkY+vzvsf6DZGsGLIB2yjn4Alxo/PQUqmxSQY4Dx1kB9+ZMJQD3fkpO4D\nv4Kmo7vi7Jwr23p3AHZgnhduXij02fIWuSNOEutfAoGAdgIAT/crn7ukTGjCKbsr\nNz0Fak3hek5u8iBBELj3+2vwW5NWewooMvGyxboxx/XxrkV5C5yhhCUg+S3jcfeB\nWiPE4qSj80Ij9P8o2S47gKbP76V2P96tzRjWex9Cpqhx/0FrkFCWEYWlOL+gXOaa\nfQABZgOsS3YkigAkwymeX3kCgYALDzElBJfK4z9vLbyPGFQk+caW5sKC19MBHRCJ\nWohUyJUGE5+AQ+ftBq6aTZ+gB0W6OkxPZpesC5n1+qikTzyaoAoU4qwYHHE/n9+y\nALDoYso8pvEiNHCudElw6VKVJ9FkVe2Sh443Zh5o/8XK8ZijDfaT1m2P24HLKh+o\nriA9/QKBgQDY4ZwBwr9N6ZubN1sIBUtDF1Jbey5aaknLPtwkxGTUkSXtRN2v+vXC\n1e6Qs1BT5t8oTgXBogicJIexhEsAGkcKM0Q1qEIYMbVpZ8B/MvyaV17OcAShE1d+\nuwl8griUdgU6R9v2uY3jzrfy4/vPOuW++FP/z7HY1x3mBHXqqsfkgg==\n-----END RSA PRIVATE KEY-----
#     key_pair = KeyPairs(**{'name': data.get('key'),
#                            "material": data.get('value'),
#                            'extension': 'pem'})
#     db.session.add(key_pair)
#     db.session.commit()
#     return "ok"

@bp.delete('/dev')
def dev_del():
    client = boto3.client('ec2', region_name=REGION)
    resp = client.delete_key_pair(KeyName='easyun-dev-key')
    result = Result(detail=resp)
    return result.make_resp()

@bp.route("/free_tier")
class FreeTier(MethodView):
    def get(self):
        return "ok"

    @input(FreeTierInputSchema)
    def post(self, data:dict):
        print(data)
        # account:Account = Account.query.
        result = Result(detail=data)
        return result.make_resp()