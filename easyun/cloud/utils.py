# -*- coding: utf-8 -*-
"""
  @module:  Cloud Utils
  @desc:    存放Cloud相关公共组件
  @auth:    aleck
"""

import boto3
from easyun.common.models import Datacenter


_EASYUN_SESSION = boto3.session.Session()
_EC2_RESOURCE = None


def get_easyun_session(dc_name=None):
    '''设置Boto3 Session 默认region,返回region name'''
    global _EASYUN_SESSION
    # return current session if no dc_name is specified
    if dc_name is None:
        return _EASYUN_SESSION
    else:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
    if thisDC:
        dcRegion = thisDC.region
        # Get or Create Easyun boto3 session
        if _EASYUN_SESSION is not None and _EASYUN_SESSION.region_name == dcRegion:
            return _EASYUN_SESSION
        else:
            _EASYUN_SESSION = boto3.session.Session(region_name=dcRegion)
            return _EASYUN_SESSION
    else:
        raise ValueError(f'{dc_name} does not exist !')


def get_ec2_resource():
    global _EC2_RESOURCE
    if _EC2_RESOURCE is None:
        eySession = get_easyun_session()
        _EC2_RESOURCE = eySession.resource('ec2')
    return _EC2_RESOURCE


def gen_dc_tag(dc_name, type='flag'):
    '''生成dcName对应的tag标签'''
    if type == 'flag':
        flagTag = {"Key": "Flag", "Value": dc_name}
    elif type == 'filter':
        flagTag = {'Name': 'tag:Flag', 'Values': [dc_name]}
    return flagTag


def gen_hash_tag(dc_name, type='flag'):
    '''查询并生成dcName对应的tag标签'''
    thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
    flagHash = thisDC.get_hash()
    if type == 'flag':
        flagTag = {"Key": "Flag", "Value": flagHash}
    elif type == 'filter':
        flagTag = {'Name': 'tag:Flag', 'Values': [flagHash]}
    return flagTag


def query_dc_list():
    '''从本地数据库查询datacenter名单'''
    try:
        # dcList = Datacenter.query.with_entities(Datacenter.name).all()
        dcList = [dc.name for dc in Datacenter.query.all()]
        return dcList
    except Exception as ex:
        # return 'get datacenter list error.'
        return str(ex)


def query_dc_region(dc_name):
    '''通过dcName查询Region信息'''
    try:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
        if thisDC is None:
            raise ValueError('Datacenter not existed, kindly create it first!')
        return thisDC.region
    except Exception as ex:
        return str(ex)


def query_dc_vpc(dc_name):
    '''通过dcName查询VPC信息'''
    try:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
        return thisDC.vpc_id
    except Exception:
        return 'Datacenter not existed, kindly create it first!'


def set_boto3_region(dc_name):
    '''设置Boto3会话默认region,返回region name'''
    thisDC: Datacenter = Datacenter.query.filter_by(name=dc_name).first()
    if thisDC:
        # 设置 boto3 接口默认 region_name
        boto3.setup_default_session(region_name=thisDC.region)
        return thisDC.region
    else:
        raise ValueError(f'{dc_name} does not exist !')


def get_tag_name(res_type, res_id):
    '''通过 Resource ID 查询资源的 tag:Name'''
    resource_ec2 = get_ec2_resource()
    try:
        if res_type == 'server':
            res = resource_ec2.Instance(res_id)
        elif res_type == 'volume':
            res = resource_ec2.Volume(res_id)
        elif res_type == 'keypari':
            res = resource_ec2.KeyPair(res_id)
        elif res_type == 'subnet':
            res = resource_ec2.Subnet(res_id)
        elif res_type == 'secgroup':
            res = resource_ec2.SecurityGroup(res_id)
        elif res_type == 'igw':
            res = resource_ec2.InternetGateway(res_id)
        elif res_type == 'natgw':
            return 'Nat Gateway'
        elif res_type == 'route':
            res = resource_ec2.Route(res_id)
        elif res_type == 'routetable':
            res = resource_ec2.RouteTable(res_id)
        else:
            raise ValueError('reasouce type error')
        tagName = next((tag['Value'] for tag in res.tags if tag["Key"] == 'Name'), None)
        return tagName
    except Exception as ex:
        return str(ex)


def get_server_name(svr_id):
    '''通过instanceID 查询服务器 tag:Name'''
    try:
        if svr_id is None:
            raise ValueError('svr_id is None')
        # server = resource_ec2.Instance(svr_id)
        # tagName = next((tag['Value'] for tag in server.tags if tag["Key"] == 'Name'), None)
        tagName = get_tag_name('server', svr_id)
        return tagName
    except Exception:
        return None


def get_eni_type(eni_id):
    '''获取 Elastic Network Interface 类型'''
    # 'InterfaceType': 'interface'|'natGateway'|'efa'|'trunk'|'load_balancer'|'network_load_balancer'|'vpc_endpoint'|'transit_gateway',
    resource_ec2 = get_ec2_resource()
    try:
        if eni_id is None:
            raise ValueError('subnet_id is None')
        thisEni = resource_ec2.NetworkInterface(eni_id)
        return thisEni.interface_type
    except Exception as ex:
        return str(ex)


def get_subnet_type(subnet_id):
    '''判断subnet type是 public 还是 private'''
    # 偷个懒仅以名称判断，完整功能待实现
    resource_ec2 = get_ec2_resource()
    try:
        if subnet_id == None:
            raise ValueError('subnet_id is None')
        thisSubnet = resource_ec2.Subnet(subnet_id)
        nameTag = next(
            (tag['Value'] for tag in thisSubnet.tags if tag["Key"] == 'Name'), None
        )
        if nameTag.lower().startswith('pub'):
            subnetType = 'public'
        elif nameTag.lower().startswith('pri'):
            subnetType = 'private'
        else:
            subnetType = 'unknown'
        return subnetType
    except Exception as ex:
        return str(ex)
