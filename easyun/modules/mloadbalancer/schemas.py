# encoding: utf-8
"""
  @module:  LoadBalancer Schema
  @desc:    LoadBalancer Input/output schema
"""

from apiflask import Schema
from apiflask.fields import String, List, Dict, Nested
from easyun.common.schemas import TagItem


class ElbAzItem(Schema):
    azName = String(metadata={"example": "us-east-1a"})
    subnetId = String(metadata={"example": "subnet-0abcdef"})
    elbAddresses = List(Dict())


class ElbDetailItem(Schema):
    elbId = String(attribute='id', metadata={"example": "my-alb"})
    dnsName = String(attribute='dns_name', metadata={"example": "my-alb-123456.us-east-1.elb.amazonaws.com"})
    elbArn = String(attribute='arn')
    elbAzs = List(Nested(ElbAzItem), attribute='azs')
    ipType = String(attribute='ip_type', metadata={"example": "ipv4"})
    elbType = String(attribute='lb_type', metadata={"example": "application"})
    elbState = String(attribute='state', metadata={"example": "active"})
    elbScheme = String(attribute='scheme', metadata={"example": "internet-facing"})
    secGroups = List(String(), attribute='security_groups')
    createTime = String(attribute='create_time')


class ElbBriefItem(Schema):
    elbId = String(attribute='id', metadata={"example": "my-alb"})
    elbArn = String(attribute='arn')
    dnsName = String(attribute='dns_name')
    elbType = String(attribute='lb_type', metadata={"example": "application"})
    elbState = String(attribute='state', metadata={"example": "active"})
    elbScheme = String(attribute='scheme', metadata={"example": "internet-facing"})


class ElbBasic(Schema):
    elbId = String(metadata={"example": "my-alb"})
    tagName = String(metadata={"example": "my-load-balancer"})
    dnsName = String(metadata={"example": "my-alb-123456.us-east-1.elb.amazonaws.com"})
    elbType = String(metadata={"example": "application"})
    elbState = String(metadata={"example": "active"})
    elbScheme = String(metadata={"example": "internet-facing"})


class ElbDetail(Schema):
    elbBasic = Nested(ElbBasic)
    elbListeners = List(Dict())
    elbConfig = Dict()
    elbProperty = Dict()
    userTags = List(Nested(TagItem))
