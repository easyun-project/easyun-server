# encoding: utf-8
"""
  @module:  LoadBalancer Schema
  @desc:    LoadBalancer Input/output schema
"""

from apiflask import Schema
from apiflask.fields import String, List, Dict, Nested


class ElbAzItem(Schema):
    azName = String(metadata={"example": "us-east-1a"})
    subnetId = String(metadata={"example": "subnet-0abcdef"})
    elbAddresses = List(Dict())


class ElbDetailItem(Schema):
    elbId = String(metadata={"example": "my-alb"})
    dnsName = String(metadata={"example": "my-alb-123456.us-east-1.elb.amazonaws.com"})
    elbArn = String()
    elbAzs = List(Nested(ElbAzItem))
    ipType = String(metadata={"example": "ipv4"})
    elbType = String(metadata={"example": "application"})
    elbState = String(metadata={"example": "active"})
    elbScheme = String(metadata={"example": "internet-facing"})
    secGroups = List(String())
    createTime = String()


class ElbBriefItem(Schema):
    elbId = String(metadata={"example": "my-alb"})
    elbArn = String()
    dnsName = String()
    elbType = String(metadata={"example": "application"})
    elbState = String(metadata={"example": "active"})
    elbScheme = String(metadata={"example": "internet-facing"})
