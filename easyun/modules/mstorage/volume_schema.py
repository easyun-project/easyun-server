# encoding: utf-8
"""
  @module:  Block Storage Schema
  @desc:    块存储(EBS) 资源管理Schema定义
  @auth:    
"""

from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length


class newVolume(Schema):
    az = String(required=True)
    instanceId = String(required=True)
    diskType = String(required=True)
    size = String(required=True)
    iops = String(required=True)
    thruput = String(required=True)
    diskPath = String(required=True)
    encryption = String(required=True)