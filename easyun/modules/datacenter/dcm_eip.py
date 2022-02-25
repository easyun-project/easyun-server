# -*- coding: utf-8 -*-
"""
  @desc:    DataCenter module mock API
  @LastEditors: aleck
"""

from email import message
import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp,DryRun
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameQuery
from easyun.common.utils import gen_dc_tag
from .schemas import DataCenterEIPIn,DataCenterNewEIPIn,DataCenterListsIn,DataCenterListIn,DcParmIn,DataCenterSubnetIn


@bp.get('/eip')
@auth_required(auth_token)
# @input(DataCenterEIPIn, location='query')
@input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_eip_detail(param):
    '''获取 全部静态IP(EIP)信息'''
    # only for globa regions
    # dc_name=request.args.get("vpc_idp")
    # dcTag = {"Key": "Flag", "Value": dcName}

    dcName=param.get('dc')
    
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    # if (thisDC is None):
    #         response = Result(detail ={'Result' : 'Errors'}, message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
    #         response.err_resp()   
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    try:
        eips = client_ec2.describe_addresses(
            Filters=[
                gen_dc_tag(dcName, 'filter'),
            ]
        )['Addresses']

        eipList = []    

        for eip in eips:
            nameTag = next((tag['Value'] for tag in eip.get('Tags') if tag["Key"] == 'Name'), None)
            eipItem = {
                'pubIp': eip['PublicIp'],
                'tagName': nameTag,                
                'alloId': eip['AllocationId'],
                'eipDomain': eip['Domain'],
                'ipv4Pool': eip['PublicIpv4Pool'],
                'boarderGroup' : eip['NetworkBorderGroup'],
                #可基于AssociationId判断eip是否可用
                'assoId': eip.get('AssociationId'),
                #eip关联的目标ID及Name
                'targetId' : eip.get('InstanceId'),
                # 'targetName': 'server_name_xxx',
                'eniId': eip.get('NetworkInterfaceId')                
            }
            eipList.append(eipItem)

        resp = Result(
            detail = eipList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=ex, status_code=2101,http_status_code=400)
        resp.err_resp()


@bp.get('/eip/<pub_ip>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def get_eip_detail(pub_ip, param):
    '''获取 指定静态IP(EIP)信息'''

    dcName = param.get('dc')
    try:
        thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
        client_ec2 = boto3.client('ec2', region_name= thisDC.region)
        eips = client_ec2.describe_addresses(
            Filters=[
                gen_dc_tag(dcName, 'filter'),
            ],
            PublicIps = [pub_ip],
            # AllocationIds=[ eip_id ]
        )

        # 从describe_addresses返回结果筛选出所需的字段
        eip = eips.get('Addresses')[0]

        if eip:
            nameTag = next((tag['Value'] for tag in eip.get('Tags') if tag["Key"] == 'Name'), None)
            eipAttributes = {
                'pubIp': eip['PublicIp'],
                'tagName': nameTag,                
                'alloId': eip['AllocationId'],
                'eipDomain': eip['Domain'],
                'ipv4Pool': eip['PublicIpv4Pool'],
                'boarderGroup' : eip['NetworkBorderGroup'],
                #可基于AssociationId判断eip是否可用
                'assoId': eip.get('AssociationId'),
                #eip关联的目标ID及Name                
                'targetId' : eip.get('InstanceId'),
                'targetName': 'server_name_xxx',
                'eniId': eip.get('NetworkInterfaceId')                
            }            

        resp = Result(
            detail = eipAttributes,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=ex, status_code=2101,http_status_code=400)
        resp.err_resp()


@bp.get('/eip/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_eip_brief(param):
    '''获取 全部静态IP列表(EIP)[仅基础字段]'''
    dcName=param.get('dc')  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    try:
        eips = client_ec2.describe_addresses(
            Filters=[
                { 'Name': 'tag:Flag', 'Values': [dcName] },             
            ]
        )['Addresses']

        eipList = []

        for eip in eips:
            # nameTag = [tag['Value'] for tag in eip.get('Tags') if tag['Key'] == 'Name']
            nameTag = next((tag['Value'] for tag in eip.get('Tags') if tag['Key'] == 'Name'), None)
            eipItem = {
                'pubIp': eip['PublicIp'],
                'alloId': eip['AllocationId'],
                # 'tagName': nameTag[0] if len(nameTag) else None
                'tagName': nameTag,          
                #可基于AssociationId判断eip是否可用
                'assoId': eip.get('AssociationId'),
                'isAvailable': True if not eip.get('AssociationId') else False
            }
            eipList.append(eipItem)

        resp = Result(
            detail = eipList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=ex, status_code=2101,http_status_code=400)
        resp.err_resp()


@bp.delete('/eip')
@auth_required(auth_token)
@input(DataCenterEIPIn)
def delete_eip(param):
    '''删除 指定静态IP(EIP)'''

    dcName=param.get('dcName')
    alloId=param.get('alloId')
  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    try:
        response = client_ec2.release_address(AllocationId=alloId,DryRun=DryRun)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = Result(
                # detail = [{'AllocationId': eipId}],
                detail = alloId+' Static IP released.',
                status_code = 200 
            )
            return resp.make_resp()
        else:
            resp = Result(detail=[], status_code=2061)
            resp.err_resp()

    except Exception as ex:
        resp = Result(
            # message='release_address failed due to wrong AllocationId' ,
            message=ex,
            status_code=2061,
            http_status_code=400)
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()


@bp.post('/eip')
@auth_required(auth_token)
@input(DataCenterNewEIPIn)
# @output(DcResultOut, 201, description='add A new Datacenter')
def add_eip(param):
    '''新增 静态IP(EIP)'''
    dcName=param.get('dcName') 
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()

    # if (thisDC is None):
    #         response = Result(detail ={'Result' : 'Errors'}, message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
    #         response.err_resp() 
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)
    
    dcTag = {"Key": "Flag", "Value": dcName}

    try:
        nameTag = {"Key": "Name", "Value": dcName.lower()+"-extra-eip"}
        eip = client_ec2.allocate_address(
            DryRun=DryRun,
            Domain='vpc',
            TagSpecifications = [
                {
                    'ResourceType':'elastic-ip', 
                    "Tags": [dcTag, nameTag]
                }
            ]
        )
        
        eipList = [
            {
                'pubIp' : eip['PublicIp'],
                'alloId' : eip['AllocationId']
            } ]

        resp = Result(
            detail = eipList,
            status_code = 200 
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message='EIP creation failed', 
            status_code=2061,
            http_status_code=400)
        resp.err_resp()
