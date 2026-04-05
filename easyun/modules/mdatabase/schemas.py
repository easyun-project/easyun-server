# encoding: utf-8
"""
  @module:  Database Schema
  @desc:    Database Input/output schema
"""

from apiflask import Schema
from apiflask.fields import Integer, String, Boolean


class DbiDetailItem(Schema):
    dbiId = String(metadata={"example": "mydb-instance"})
    dbiEngine = String(metadata={"example": "mysql"})
    engineVer = String(metadata={"example": "8.0.32"})
    dbiStatus = String(metadata={"example": "available"})
    dbiSize = String(metadata={"example": "db.t3.micro"})
    vcpuNum = Integer(metadata={"example": 1})
    ramSize = Integer(metadata={"example": 2})
    volumeSize = Integer(metadata={"example": 20})
    dbiAz = String(metadata={"example": "us-east-1a"})
    multiAz = Boolean()
    dbiEndpoint = String(metadata={"example": "mydb.xxxx.us-east-1.rds.amazonaws.com"})


class DbiBriefItem(Schema):
    dbiId = String(metadata={"example": "mydb-instance"})
    dbiEngine = String(metadata={"example": "mysql"})
    dbiStatus = String(metadata={"example": "available"})
    dbiSize = String(metadata={"example": "db.t3.micro"})
    dbiAz = String(metadata={"example": "us-east-1a"})
