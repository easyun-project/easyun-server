# encoding: utf-8
"""
  @module:  Database Schema
  @desc:    Database Input/output schema
"""

from apiflask import Schema
from apiflask.fields import Integer, String, Boolean


class DbiDetailItem(Schema):
    dbiId = String(attribute='id', metadata={"example": "mydb-instance"})
    dbiEngine = String(attribute='engine', metadata={"example": "mysql"})
    engineVer = String(attribute='engine_version', metadata={"example": "8.0.32"})
    dbiStatus = String(attribute='status', metadata={"example": "available"})
    dbiSize = String(attribute='instance_class', metadata={"example": "db.t3.micro"})
    vcpuNum = Integer(attribute='vcpu', metadata={"example": 1})
    ramSize = Integer(attribute='memory_gib', metadata={"example": 2})
    volumeSize = Integer(attribute='storage_gib', metadata={"example": 20})
    dbiAz = String(attribute='az', metadata={"example": "us-east-1a"})
    multiAz = Boolean(attribute='multi_az')
    dbiEndpoint = String(attribute='endpoint', metadata={"example": "mydb.xxxx.us-east-1.rds.amazonaws.com"})


class DbiBriefItem(Schema):
    dbiId = String(attribute='id', metadata={"example": "mydb-instance"})
    dbiEngine = String(attribute='engine', metadata={"example": "mysql"})
    dbiStatus = String(attribute='status', metadata={"example": "available"})
    dbiSize = String(attribute='instance_class', metadata={"example": "db.t3.micro"})
    dbiAz = String(attribute='az', metadata={"example": "us-east-1a"})
