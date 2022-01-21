# -*- coding: utf-8 -*-

from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length
class newBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )
    versioningConfiguration = String(required=True)
    bucketEncryption = String(required=True)
    region = String(required=True)

class deleteBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )

class vaildateBucket(Schema):
    bucketName = String(
        required=True, 
        validate=Length(0, 30)
    )