# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

from apiflask import APIBlueprint
from easyun.common.auth import auth_token
from easyun.common.schemas import DcNameQuery
from easyun.common.result import Result
from easyun.cloud.aws import get_datacenter, get_subnet
from .schemas import AddSubnetParm, DelSubnetParm, SubnetBasic, SubnetModel, SubnetDetail


bp = APIBlueprint('Subnet', __name__, url_prefix='/subnet')


@bp.get('')
@bp.auth_required(auth_token)
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(SubnetModel(many=True), description='List DataCenter Subnets Resources')
def list_subnet_detail(parm):
    '''获取 全部subnet子网信息'''
    dcName = parm['dc']
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
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(SubnetBasic(many=True), description='List DataCenter Subnets Resources')
def list_subnet_brief(parm):
    '''获取 全部subnet子网列表[仅基础字段]'''
    dcName = parm['dc']
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
@bp.input(DcNameQuery, location='query', arg_name='parm')
@bp.output(SubnetDetail, description='List DataCenter Subnets Resources')
def get_subnet_detail(subnet_id, parm):
    '''获取 指定subnet子网详细信息'''
    dcName = parm['dc']
    try:
        subnet = get_subnet(subnet_id, dcName)
        subnetDetail = subnet.get_detail()
        resp = Result(detail=subnetDetail, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=2031)
        resp.err_resp()


@bp.delete('')
@bp.auth_required(auth_token)
@bp.input(DelSubnetParm, arg_name='parms')
def delete_subnet(parms):
    '''删除 指定子网subnet'''
    dcName = parms['dcName']
    subnetId = parms['subnetId']
    try:
        subnet = get_subnet(subnetId, dcName)
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
def add_subnet(parms):
    '''新增 子网Subnet'''
    dcName = parms['dcName']
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
# @input(DataCenterSubnetInsert)
# @output(DcResultOut, 201, description='add A new Datacenter')
def mod_subnet(param):
    '''修改数据中心Subnet 【to-be-done】'''

    resp = Result(detail={"subnetId", 'subnet-123456'}, status_code=200)
    return resp.make_resp()
