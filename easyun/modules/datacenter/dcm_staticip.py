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
from easyun.common.schemas import DcNameQuery, DcNameParm
from easyun.cloud.utils import gen_dc_tag, set_boto3_region, get_tag_name, get_eni_type
from .schemas import DelEipParm, DataCenterListsIn,DataCenterListIn,DcParmIn,DataCenterSubnetIn


@bp.get('/eip')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def list_eip_detail(param):
    '''获取 全部静态IP(EIP)信息'''
    dcName=param.get('dc')
    
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    # if (thisDC is None):
    #         response = Result(detail ={'Result' : 'Errors'}, message='DC not existed, kindly create it first!', status_code=2011,http_status_code=400)
    #         response.err_resp()  
    dcRegion = set_boto3_region(dcName) 

    try:
        client_ec2 = boto3.client('ec2' )
        eips = client_ec2.describe_addresses(
            Filters=[
                gen_dc_tag(dcName, 'filter'),
            ]
        )['Addresses']

        eipList = []    

        for eip in eips:
            nameTag = next((tag['Value'] for tag in eip.get('Tags') if tag["Key"] == 'Name'), None)
            eniType = get_eni_type( eip.get('NetworkInterfaceId') )
            eipItem = {
                'pubIp': eip['PublicIp'],
                'tagName': nameTag,
                'alloId': eip['AllocationId'],
                'eipDomain': eip['Domain'],
                'ipv4Pool': eip['PublicIpv4Pool'],
                'boarderGroup' : eip['NetworkBorderGroup'],
                'assoId': eip.get('AssociationId'),
                #eip关联的目标ID及Name
                'assoTarget':{                    
                    'svrId' : eip.get('InstanceId'),
                    'tagName': get_tag_name('server', eip.get('InstanceId')) if eniType == 'interface' else get_tag_name('natgw', ''),
                    'eniId': eip.get('NetworkInterfaceId'),
                    'eniType' : get_eni_type( eip.get('NetworkInterfaceId') ) 
                }
            }
            eipList.append(eipItem)

        resp = Result(
            detail = eipList,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2101,http_status_code=400)
        resp.err_resp()


@bp.get('/eip/<pub_ip>')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
# @output(SubnetsOut, description='List DataCenter Subnets Resources')
def get_eip_detail(pub_ip, param):
    '''获取 指定静态IP(EIP)信息'''

    dcName = param.get('dc')
    filterTag = gen_dc_tag(dcName, 'filter')
    try:
        client_ec2 = boto3.client('ec2')
        eips = client_ec2.describe_addresses(
            Filters=[ filterTag ],
            PublicIps = [pub_ip],
            # AllocationIds=[ eip_id ]
        )

        # 从describe_addresses返回结果筛选出所需的字段
        eip = eips.get('Addresses')[0]

        if eip:
            nameTag = next((tag['Value'] for tag in eip.get('Tags') if tag["Key"] == 'Name'), None)
            eniType = get_eni_type( eip.get('NetworkInterfaceId') )
            eipAttributes = {
                'pubIp': eip['PublicIp'],
                'tagName': nameTag,                
                'alloId': eip['AllocationId'],
                'eipDomain': eip['Domain'],
                'ipv4Pool': eip['PublicIpv4Pool'],
                'boarderGroup' : eip['NetworkBorderGroup'],
                'assoId': eip.get('AssociationId'),
                #eip关联的目标ID及Name
                'assoTarget':{
                    'svrId' : eip.get('InstanceId'),
                    'tagName': get_tag_name('server', eip.get('InstanceId')) if eniType == 'interface' else get_tag_name('natgw', ''),
                    'eniId': eip.get('NetworkInterfaceId'),
                    'eniType' : eniType
                },
                #基于AssociationId判断 eip是否可用
                'isAvailable': True if not eip.get('AssociationId') else False,                
            }

        resp = Result(
            detail = eipAttributes,
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message=str(ex), 
            status_code=2101,
            http_status_code=400
        )
        resp.err_resp()


@bp.get('/eip/list')
@auth_required(auth_token)
@input(DcNameQuery, location='query')
def list_eip_brief(param):
    '''获取 全部静态IP列表(EIP)[仅基础字段]'''
    dcName=param.get('dc')  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    dcRegion = set_boto3_region(dcName) 

    try:
        client_ec2 = boto3.client('ec2')
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
        resp = Result(
            message=str(ex), 
            status_code=2101,
            http_status_code=400)
        resp.err_resp()



@bp.post('/eip')
@auth_required(auth_token)
@input(DcNameParm)
# @output(DcResultOut, 201, description='add A new Datacenter')
def add_eip(param):
    '''新增 静态IP(EIP)'''
    dcName=param.get('dcName') 
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
  
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)
    
    flagTag = {"Key": "Flag", "Value": dcName}
    nameTag = {"Key": "Name", "Value": dcName.lower()+"-extra-eip"}

    try:        
        eip = client_ec2.allocate_address(
            DryRun=DryRun,
            Domain='vpc',
            TagSpecifications = [
                {
                    'ResourceType':'elastic-ip', 
                    "Tags": [flagTag, nameTag]
                }
            ]
        )        
        eipItem = {
            'pubIp' : eip['PublicIp'],
            'alloId' : eip['AllocationId']
        }

        resp = Result(
            detail = eipItem,
            status_code = 200 
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message= str(ex), 
            status_code=2061,
            http_status_code=400)
        resp.err_resp()


@bp.delete('/eip')
@auth_required(auth_token)
@input(DelEipParm)
def delete_eip(parm):
    '''删除 指定静态IP(EIP)'''

    dcName=parm.get('dcName')
    alloId=parm.get('alloId')
  
    thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
    client_ec2 = boto3.client('ec2', region_name= thisDC.region)

    try:
        response = client_ec2.release_address(
            AllocationId=alloId,
            DryRun=DryRun
        )
        resp = Result(
            # detail = [{'AllocationId': eipId}],
            detail = f'{alloId} Static IP(EIP) released',
            status_code = 200 
        )
        return resp.make_resp()


    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=2061,
            http_status_code=400)
        # resp = Result(message=ex, status_code=2061,http_status_code=400)
        resp.err_resp()
