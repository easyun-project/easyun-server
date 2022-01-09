# -*- coding: utf-8 -*-
'''
    :file: schema.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2021/12/22 17:24:44
'''

from apiflask import Schema
from apiflask.fields import String, Integer


class CreateSSHKeySchema(Schema):
    region = String(example="us-east-1")
    key_name = String(example="easyun-dev-key")

class AWSInfoOutSchema(Schema):
    account_id = String()
    aws_type = String()
    role = String()

class SSHKeysOutputSchema(Schema):
    id = Integer()
    region = String()
    name = String(data_key='key_name')