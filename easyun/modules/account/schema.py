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
        required=True, validate=Length(0, 60), metadata={"example": "Easyun"}  # Datacenter name
    )
    keyName = String(
        required=True, validate=Length(0, 255), metadata={"example": 'easyun-dev-key'}  # Keypair name
    )
    keyType = String(
        required=False, validate=OneOf('rsa', 'ed25519'), metadata={"example": 'rsa'}  # Keypair type
    )


class KeyPairDelIn(Schema):
    dcName = String(
        required=True, validate=Length(0, 60), metadata={"example": "Easyun"}  # Datacenter name
    )
    keyName = String(
        required=True, validate=Length(0, 255), metadata={"example": 'easyun-dev-key'}  # Keypair name
    )


class KeypairOut(Schema):
    keyName = String(attribute='name', required=True, metadata={"example": 'easyun-dev-key'})
    keyType = String(attribute='key_type', required=False, metadata={"example": 'rsa'})
    keyFingerprint = String(attribute='fingerprint')
    keyTags = List(Dict(), attribute='tags')
    keyRegion = String()  # 由 API 层附加，不在 dataclass 里


class CreateSSHKeySchema(Schema):
    region = String(metadata={"example": "us-east-1"})
    keyName = String(metadata={"example": "easyun-dev-key"})


class AWSAccountInfo(Schema):
    accountId = String()
    awsType = String()
    role = String()


class SSHKeysOutputSchema(Schema):
    id = Integer()
    region = String()
    name = String(data_key='keyName')


class FreeTierQuery(Schema):
    accountId = String(metadata={"example": '567820211120'})


class FreeTierParm(Schema):
    isReminderOn = Boolean(required=True, metadata={"example": True})
    activeDate = Date(required=True)
    accountId = String(metadata={"example": '567820211120'})


class FreeTierInfo(Schema):
    isReminderOn = Boolean(metadata={"example": True})
    activeDate = Date(metadata={"example": '2022-02-27'})
    remainDays = Integer(metadata={"example": 180})
    iconColor = String(metadata={"example": "green"})


class QuotaItem(Schema):
    quotaName = String()
    quotaCode = String()
    quotaValue = Integer()
    usageValue = Integer()
    serviceName = String()
