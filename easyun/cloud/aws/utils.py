# -*- coding: utf-8 -*-
"""
  @module:  AWS Utils
  @desc:    AWS SDK 相关工具函数
  @auth:    aleck
"""

from easyun.cloud.aws.session import get_easyun_session


# 定义系统盘路径
SYSTEM_DISK = ['/dev/xvda', '/dev/sda1']


def get_imds_region():
    """通过 IMDSv2 获取 EC2 实例所在 region"""
    import urllib.request
    token_url = 'http://169.254.169.254/latest/api/token'
    req = urllib.request.Request(token_url, method='PUT')
    req.add_header('X-aws-ec2-metadata-token-ttl-seconds', '30')
    token = urllib.request.urlopen(req, timeout=2).read().decode()

    az_url = 'http://169.254.169.254/latest/meta-data/placement/availability-zone'
    req = urllib.request.Request(az_url)
    req.add_header('X-aws-ec2-metadata-token', token)
    az = urllib.request.urlopen(req, timeout=2).read().decode()
    return az[:-1]


def get_ec2_resource():
    session = get_easyun_session()
    return session.resource('ec2')


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
        return get_tag_name('server', svr_id)
    except Exception:
        return None


def get_disk_type(attach_path):
    diskType = 'system' if attach_path in SYSTEM_DISK else 'user'
    return diskType


def get_eni_type(eni_id):
    '''获取 Elastic Network Interface 类型'''
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
    resource_ec2 = get_ec2_resource()
    try:
        if subnet_id is None:
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
