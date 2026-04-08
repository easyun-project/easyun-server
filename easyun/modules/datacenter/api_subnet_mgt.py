# -*- coding: utf-8 -*-
"""
  @module:
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

from apiflask import APIBlueprint
from easyun.common.auth import auth_token
from easyun.common.schemas import get_dc_name
from easyun.common.result import Result
from easyun.cloud import get_datacenter
from .schemas import DcMsgOut, AddSubnetParm, DelSubnetParm, ModSubnetParm, SubnetBasic, SubnetModel, SubnetDetail


bp = APIBlueprint('Subnet', __name__, url_prefix='/subnet')


@bp.get('')
@bp.auth_required(auth_token)
@bp.output(SubnetModel(many=True), description='List DataCenter Subnets Resources')
def list_subnet_detail():
    '''获取 全部subnet子网信息'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        subnetList = dc.list_all_subnet()
        resp = Result(detail=subnetList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(detail=str(ex), status_code=2101)
        resp.err_resp()


@bp.get('/list')
@bp.auth_required(auth_token)
@bp.output(SubnetBasic(many=True), description='List DataCenter Subnets Resources')
def list_subnet_brief():
    '''获取 全部subnet子网列表[仅基础字段]'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        subnetList = dc.get_subnet_list()
        resp = Result(detail=subnetList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(detail=str(ex), status_code=2102)
        resp.err_resp()


@bp.get('/<subnet_id>')
@bp.auth_required(auth_token)
@bp.output(SubnetDetail, description='List DataCenter Subnets Resources')
def get_subnet_detail(subnet_id):
    '''获取 指定subnet子网详细信息'''
    dcName = get_dc_name()
    try:
        dc = get_datacenter(dcName)
        subnet = dc.get_subnet(subnet_id)
        subnetDetail = subnet.get_detail()
        resp = Result(detail=subnetDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.delete('')
@bp.auth_required(auth_token)
@bp.input(DelSubnetParm, arg_name='parms')
@bp.output(DcMsgOut)
def delete_subnet(parms):
    '''删除 指定子网subnet'''
    dcName = get_dc_name()
    subnetId = parms['subnetId']
    try:
        dc = get_datacenter(dcName)
        subnet = dc.get_subnet(subnetId)
        oprtRes = subnet.delete()
        resp = Result(detail=oprtRes, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2061)
        resp.err_resp()


@bp.post('')
@bp.auth_required(auth_token)
@bp.input(AddSubnetParm, arg_name='parms')
# @output(DcResultOut, 201, description='add A new Datacenter')
@bp.output(SubnetModel)
def add_subnet(parms):
    '''新增 子网Subnet'''
    dcName = get_dc_name()
    cidrBlock = parms['cidrBlock']
    azName = parms['azName']
    tagName = parms['tagName']
    try:
        dc = get_datacenter(dcName)
        newSubnet = dc.create_subnet(cidrBlock, azName, tagName)
        resp = Result(detail=newSubnet, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2011)
        resp.err_resp()


@bp.put('')
@bp.auth_required(auth_token)
@bp.input(ModSubnetParm, arg_name='parm')
@bp.output(SubnetModel)
def mod_subnet(parm):
    '''修改数据中心 Subnet 属性'''
    dcName = get_dc_name()
    subnetId = parm['subnetId']
    try:
        dc = get_datacenter(dcName)
        subnet = dc.get_subnet(subnetId)
        client = subnet._client
        isMapPublicIp = parm.get('isMapPublicIp')
        if isMapPublicIp is not None:
            client.modify_subnet_attribute(
                SubnetId=subnetId,
                MapPublicIpOnLaunch={'Value': isMapPublicIp},
            )
        resp = Result(detail={
            'subnetId': subnetId,
            'isMapPublicIp': isMapPublicIp,
        }, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2051)
        resp.err_resp()
