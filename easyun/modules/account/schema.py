# -*- coding: utf-8 -*-
'''
    :file: schema.py
    :author: -Farmer
    :url: https://blog.farmer233.top
    :date: 2021/12/22 17:24:44
'''

from apiflask import Schema
from apiflask.fields import String, Integer, Date, Boolean, List, Dict
from apiflask.validators import Length, OneOf


class KeypairParms(Schema):
    dcName = String(
        required=True, validate=Length(0, 60), example="Easyun"  # Datacenter name
    )
    keyName = String(
        required=True, validate=Length(0, 255), example='easyun-dev-key'  # Keypair name
    )
    keyType = String(
        required=False, validate=OneOf('rsa', 'ed25519'), example='rsa'  # Keypair type
    )


class KeyPairDelIn(Schema):
    dcName = String(
        required=True, validate=Length(0, 60), example="Easyun"  # Datacenter name
    )
    keyName = String(
        required=True, validate=Length(0, 255), example='easyun-dev-key'  # Keypair name
    )


class KeypairOut(Schema):
    keyName = String(required=True, example='easyun-dev-key')  # Keypair name
    keyType = String(required=False, example='rsa')  # Keypair type
    keyFile = String()
    keyFingerprint = String()
    keyTags = List(Dict())
    keyRegion = String()


class CreateSSHKeySchema(Schema):
    region = String(example="us-east-1")
    key_name = String(example="easyun-dev-key")


class AWSAccountInfo(Schema):
    account_id = String()
    aws_type = String()
    role = String()


class SSHKeysOutputSchema(Schema):
    id = Integer()
    region = String()
    name = String(data_key='key_name')


class FreeTierInputSchema(Schema):
    # remind = Boolean(example=False)
    active_date = Date()


class FreeTierOutputSchema(Schema):
    remainder = Integer()
