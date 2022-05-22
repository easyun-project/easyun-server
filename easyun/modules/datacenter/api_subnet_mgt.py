# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

import boto3
from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.libs.utils import len_iter
from easyun.cloud.utils import get_subnet_type
from .schemas import DataCenterSubnetIn, DataCenterSubnetInsert
from . import bp, get_sub_net


@bp.get('/subnet/<subnet_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# # @output(SubnetsOut, description='List DataCenter Subnets Resources')
def get_subnet_detail(subnet_id, param):
    '''获取 指定subnet子网信息'''

    dcName = param.get('dc')
    try:
        thisDC: Datacenter = Datacenter.query.filter_by(name=dcName).first()
        resource_ec2 = boto3.resource('ec2', region_name=thisDC.region)
        thisSubnet = resource_ec2.Subnet(subnet_id)
        # 统计subnet下的服务器数量
        svrCollection = thisSubnet.instances.all()
        svrNum = len_iter(svrCollection)
        # 统计subnet下的网卡数量
        eniCollection = thisSubnet.network_interfaces.all()
        eniNum = len_iter(svrCollection)
        # 判断subnet type是 public 还是 private
        subnetType = get_subnet_type(subnet_id)

        subnetAttributes = {
            'tagName': [
                tag.get('Value') for tag in thisSubnet.tags if tag.get('Key') == 'Name'
            ][0],
            'subnetType': subnetType,
            'subnetState': thisSubnet.state,
            'subnetId': thisSubnet.subnet_id,
            'subnetVpc': thisSubnet.vpc_id,
            'subnetAz': thisSubnet.availability_zone,
            'cidrBlock': thisSubnet.cidr_block,
            'avlipNum': thisSubnet.available_ip_address_count,
            'isMappubip': thisSubnet.map_public_ip_on_launch,
            'svrNum': svrNum,
            'eniNum': eniNum,
        }

        resp = Result(detail=subnetAttributes, status_code=200)
        return resp.make_resp()

    except Exception as e:
        resp = Result(detail=str(e), status_code=2031)
        return resp.err_resp()



@bp.delete('/subnet')
@auth_required(auth_token)
@bp.input(DataCenterSubnetIn)
def delete_subnet(param):
    '''删除 指定subnet【未完成】'''
    dcName = param.get('dcName')
    subnetID = param.get('subnetID')

    dcTag = {"Key": "Flag", "Value": dcName}

    thisDC: Datacenter = Datacenter.query.filter_by(name=dcName).first()

    if thisDC is None:
        response = Result(
            message='DC not existed, kindly create it first!',
            status_code=2011,
            http_status_code=400,
        )
        response.err_resp()

    client_ec2 = boto3.client('ec2', region_name=thisDC.region)

    try:
        response = client_ec2.delete_subnet(SubnetId=subnetID, DryRun=DryRun)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = Result(detail=[], status_code=200)
            return resp.make_resp()
        else:
            resp = Result(detail=[], status_code=2061)
            resp.err_resp()
    except Exception as ex:
        resp = Result(
            message='delete subnet failed due to invalid subnetID',
            status_code=2061,
            http_status_code=400,
        )
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()

    resp = Result(detail="subnet id got deleted!", status_code=200)
    return resp.make_resp()


@bp.post('/subnet')
@auth_required(auth_token)
@bp.input(DataCenterSubnetInsert)
# @output(DcResultOut, 201, description='add A new Datacenter')
def add_subnet(param):
    '''新增 subnet 【未完成】'''
    dcName = param.get('dcName')
    subnetCIDR = param.get('subnetCDIR')

    dcTag = {"Key": "Flag", "Value": dcName}

    thisDC: Datacenter = Datacenter.query.filter_by(name=dcName).first()

    if thisDC is None:
        response = Result(
            message='DC not existed, kindly create it first!',
            status_code=2011,
            http_status_code=400,
        )
        response.err_resp()

    client_ec2 = boto3.client('ec2', region_name=thisDC.region)

    nameTag = {"Key": "Name", "Value": "VPC-" + dcName}

    try:
        subnetID = client_ec2.create_subnet(
            CidrBlock=subnetCIDR,
            VpcId=thisDC.vpc_id,
            TagSpecifications=[{'ResourceType': 'subnet', "Tags": [dcTag, nameTag]}],
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = Result(
                detail=[{'subnetID': subnetID['Subnet']['SubnetId']}], status_code=200
            )
            return resp.make_resp()
        else:
            resp = Result(detail=[], status_code=2061)
            resp.err_resp()
    except Exception as ex:
        resp = Result(
            message='create subnet failed due to invalid subnetID',
            status_code=2061,
            http_status_code=400,
        )
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()

    resp = Result(detail={"subnetId", 'subnet-123123'}, status_code=200)
    return resp.make_resp()


@bp.put('/subnet')
# @auth_required(auth_token)
# @input(DataCenterSubnetInsert)
# @output(DcResultOut, 201, description='add A new Datacenter')
def mod_subnet(param):
    '''修改数据中心subnet 【未完成】'''

    resp = Result(detail={"subnetId", 'subnet-123456'}, status_code=200)
    return resp.make_resp()
