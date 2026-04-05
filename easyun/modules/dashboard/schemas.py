# encoding: utf-8
"""
  @module:  Dashboard Schema
  @desc:    Dashboard Input/output schema
  @author:  aleck
"""

from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict, Date, Field, Nested, Float, Boolean
from apiflask.validators import Length, OneOf


# ---- summary/datacenter ----

class DcRegionInfo(Schema):
    icon = String(metadata={"example": "USA"})
    name = String(metadata={"example": "US East (N. Virginia)"})


class AzSummaryItem(Schema):
    azName = String(metadata={"example": "us-east-1a"})
    azStatus = String(metadata={"example": "running"})
    subnetNum = Integer(metadata={"example": 2})
    dcRegion = Nested(DcRegionInfo)


# ---- summary/health ----

class AlarmSummary(Schema):
    iaNum = Integer(metadata={"example": 0})
    okNum = Integer(metadata={"example": 3})
    isNum = Integer(metadata={"example": 1})


class DashboardItem(Schema):
    title = String(metadata={"example": "my-dashboard"})
    url = String(metadata={"example": "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=my-dashboard"})


class HealthSummaryOut(Schema):
    alarms = Nested(AlarmSummary)
    dashboards = List(Nested(DashboardItem))


# ---- summary/resource ----

class SizeValue(Schema):
    value = Float()
    unit = String(metadata={"example": "GiB"})


class ServerSumData(Schema):
    sumNum = Integer()
    runNum = Integer()
    stopNum = Integer()
    vcpuNum = Integer()
    ramSize = Nested(SizeValue)


class DatabaseSumData(Schema):
    sumNum = Integer()
    auroraNum = Integer()
    mysqlNum = Integer()
    mariaNum = Integer()
    postgreNum = Integer()
    cacheNum = Integer()
    oracleNum = Integer()
    sqlserverNum = Integer()


class NetworkSumData(Schema):
    sumNum = Integer()
    pubNum = Integer()
    priNum = Integer()
    igwNum = Integer()
    natNum = Integer()
    sgNum = Integer()


class StObjectSumData(Schema):
    sumNum = Integer()
    objSize = Nested(SizeValue)
    objNum = Integer()
    pubNum = Integer()
    encNum = Integer()


class StBlockSumData(Schema):
    sumNum = Integer()
    blcSize = Nested(SizeValue)
    useNum = Integer()
    avlNum = Integer()
    encNum = Integer()


class StFileSumData(Schema):
    sumNum = Integer()
    efsNum = Integer()
    efsSize = Nested(SizeValue)
    fsxNum = Integer()
    fsxSize = Nested(SizeValue)


class ResourceSumItem(Schema):
    type = String(metadata={"example": "server"})
    data = Field()


# ---- inventory ----

class InventoryTypeItem(Schema):
    type = String(metadata={"example": "server"})
    data = List(Field())
    msg = String(load_default=None)

