# -*- coding: utf-8 -*-
'''
    :file: schema.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2021/12/22 17:24:44
'''

from apiflask import Schema
from apiflask.fields import String

class CreateSSHKeySchema(Schema):
    key_name = String(example="easyun-dev-key")

class AWSInfoOutSchema(Schema):
    account_id = String()
    aws_type = String()
    role = String()

class SSHKeysOutputSchema(Schema):
    key_name = String()
    pem_url = String()