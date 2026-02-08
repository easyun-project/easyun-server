# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Creation
  @desc:    create some datacenter basic service, like vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

import boto3
from botocore.exceptions import ClientError
from flask import current_app
from easyun import log
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.models import Datacenter, Account
from easyun.common.schemas import TaskIdQuery
from easyun.libs.utils import len_iter
from easyun.libs.task_manager import run_async, get_task
from easyun.cloud.aws_quota import get_quota_value
from easyun.cloud.utils import set_boto3_region
from easyun.cloud.aws.sdk_tagging import ResGroupTagging
from .schemas import (
    DefaultParmQuery,
    DefaultParmsOut,
    AddDataCenterParm,
    DelDataCenterParm,
    DataCenterModel,
)
from .task_create import create_dc_task
from .task_delete import delete_dc_task
from . import bp, logger


@bp.get('/default')
@bp.auth_required(auth_token)
@bp.input(DefaultParmQuery, location='query', arg_name='parm')
@bp.output(DefaultParmsOut, description='Get DataCenter Parameters')
def get_default_parms(parm):
    '''获取创建云数据中心默认参数'''
    inputName = parm['dc']
    inputRegion = parm.get('region')
    try:
        # Check if the DC Name is available
        thisDC: Datacenter = Datacenter.query.filter_by(name=inputName).first()
        if thisDC is not None:
            raise ValueError('DataCenter name already existed')

        # tag:Name prefix for all resource, eg. easyun-xxx
        prefix = inputName.lower()

        # get account info from database
        curr_account: Account = Account.query.first()
        # set deploy_region as default region
        if inputRegion is None:
            inputRegion = curr_account.get_region()

        # get az list
        client_ec2 = boto3.client('ec2', region_name=inputRegion)
        azs = client_ec2.describe_availability_zones()
        azList = [az['ZoneName'] for az in azs['AvailabilityZones']]

        # define default vpc parameters
        defaultVPC = {
            'cidrBlock': '10.10.0.0/16',
            # 'vpcCidrv6' : '',
            # 'vpcTenancy' : 'Default',
        }

        # define default igw
        defaultIgw = {
            # 这里为igw的 tag:Name，创建首个igw的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'igw')
        }

        # define default natgw
        defaultNatgw = {
            # 这里为natgw的 tag:Name ，创建首个natgw的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'natgw')
        }

        gwList = [defaultIgw["tagName"], defaultNatgw["tagName"]]

        # define default igw route table
        defaultIrtb = {
            # 这里为igw routetable 的 tag:Name, 创建首个igw routetable 的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'rtb-igw')
        }

        # define default natgw route table
        defaultNrtb = {
            # 这里为nat routetable 的 tag:Name ，创建首个nat routetable 的时候默认该名称
            "tagName": '%s-%s'
            % (prefix, 'rtb-natgw')
        }

        rtbList = [defaultIrtb["tagName"], defaultNrtb["tagName"]]

        dcParms = {
            # default selected parameters
            "dcName": inputName,
            "dcRegion": inputRegion,
            'dcVPC': defaultVPC,
            "pubSubnet1": {
                "tagName": "Public subnet 1",
                "cidrBlock": "10.10.1.0/24",
                "azName": azList[0],
                "gwName": defaultIgw["tagName"],
                "routeTable": defaultIrtb["tagName"],
            },
            "pubSubnet2": {
                "tagName": "Public subnet 2",
                "cidrBlock": "10.10.2.0/24",
                "azName": azList[1],
                "gwName": defaultIgw["tagName"],
                "routeTable": defaultIrtb["tagName"],
            },
            "priSubnet1": {
                "tagName": "Private subnet 1",
                "cidrBlock": "10.10.21.0/24",
                "azName": azList[0],
                "gwName": defaultNatgw["tagName"],
                "routeTable": defaultNrtb["tagName"],
            },
            "priSubnet2": {
                "tagName": "Private subnet 2",
                "cidrBlock": "10.10.22.0/24",
                "azName": azList[1],
                "gwName": defaultNatgw["tagName"],
                "routeTable": defaultNrtb["tagName"],
            },
            "securityGroup0": {
                "tagName": '%s-%s' % (prefix, 'sg-default'),
                # 该标记对应是否增加 In-bound: Ping 的安全组规则
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False,
            },
            "securityGroup1": {
                "tagName": '%s-%s' % (prefix, 'sg-webapp'),
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False,
            },
            "securityGroup2": {
                "tagName": '%s-%s' % (prefix, 'sg-database'),
                "enablePing": True,
                "enableSSH": True,
                "enableRDP": False,
            },
        }
        dropDown = {
            # for DropDownList
            "azList": azList,
            "gwList": gwList,
            "rtbList": rtbList,
        }

        response = Result(
            detail={'dcParms': dcParms, 'dropDown': dropDown}, status_code=200
        )
        return response.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2005, http_status_code=400)
        resp.err_resp()


@bp.post('')
@bp.auth_required(auth_token)
@bp.input(AddDataCenterParm, arg_name='parm')
@log.api_error(logger)
def create_dc_async(parm):
    '''创建 Datacenter 及基础资源[异步]'''
    dcName = parm['dcName']
    dcRgeion = parm['dcRegion']

    # Check the prerequisites before create datacenter task
    try:
        boto3.setup_default_session(region_name=dcRgeion)
        resource_ec2 = boto3.resource('ec2')

        # Check if the DC Name is available
        thisDC: Datacenter = Datacenter.query.filter_by(name=dcName).first()
        if thisDC is not None:
            raise ValueError('DataCenter name already existed')
        # Check if VPC quota is enough
        vpcQuota = get_quota_value('vpc', 'L-F678F1CE')
        vpcIter = resource_ec2.vpcs.all()
        if len_iter(vpcIter) >= int(vpcQuota):
            raise ValueError('The VPCs per Region limit has been reached')
        # Check if EIP quota is enough
        eipQuota = get_quota_value('ec2', 'L-0263D0A3')
        eipIter = resource_ec2.vpc_addresses.all()
        if len_iter(eipIter) >= int(eipQuota):
            raise ValueError('The EC2-VPC Elastic IPs limit has been reached')

    except Exception as ex:
        logger.error('[DataCenter]' + str(ex))
        resp = Result(message=str(ex), status_code=2001)
        resp.err_resp()

    # create a datacenter creation async task
    try:
        currUser = auth_token.current_user.username
        task = run_async(create_dc_task, current_app._get_current_object(), parm, currUser)
        resp = Result(
            task={
                'taskId': task.id,
                'status': task.status,
            },
            status_code=200,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2003)
        resp.err_resp()


@bp.delete('')
@bp.auth_required(auth_token)
@bp.input(DelDataCenterParm, arg_name='parm')
@log.api_error(logger)
def delete_dc_async(parm):
    '''删除 Datacenter 及基础资源[异步]'''
    dcName = parm['dcName']
    isForceDel = parm.get('isForceDel')
    # Check the prerequisites before create datacenter task
    try:
        dcRegion = set_boto3_region(dcName)
        rgt = ResGroupTagging(dcName)
        # step 1: DC resource empty checking - instance
        serverNum = rgt.sum_resources('ec2:instance')
        if serverNum > 0:
            raise ValueError(
                f'DataCenter NOT Empty, contains {serverNum} Server(s) resources.'
            )

        # step 2: DC resource empty checking - volume
        volumeNum = rgt.sum_resources('ec2:volume')
        if volumeNum > 0:
            raise ValueError(
                f'DataCenter NOT Empty, contains {volumeNum} Volume(s) resources.'
            )

        # step 3: DC resource empty checking - rds
        rdsNum = rgt.sum_resources('rds:db')
        if rdsNum > 0:
            raise ValueError(
                f'DataCenter NOT Empty, contains {rdsNum} Database(s) resources.'
            )

    except Exception as ex:
        logger.error(f'[DataCenter] {str(ex)}')
        resp = Result(message=f'[DataCenter] {str(ex)}', status_code=2011)
        resp.err_resp()

    # step 4: DC resource empty checking - NAT Gateway
    if not isForceDel:
        natgwNum = rgt.sum_resources('ec2:natgateway')
        if natgwNum > 0:
            resp = Result(
                message=f'{natgwNum} NatGateway(s) associated with the Datacenter. Set isForceDel=true to force delete.',
                status_code=2012,
                http_status_code=409,
            )
            resp.err_resp()

    # create a datacenter delete async task
    try:
        task = run_async(delete_dc_task, current_app._get_current_object(), parm, dcRegion)
        resp = Result(
            task={
                'taskId': task.id,
                'status': task.status,
            },
            status_code=200,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=2013)
        resp.err_resp()


@bp.get('/task')
@bp.auth_required(auth_token)
@bp.input(TaskIdQuery, location='query', arg_name='parm')
@bp.output(DataCenterModel)
def get_task_result(parm):
    '''获取异步任务执行结果'''
    task_id = parm['id'].replace('_', '-')
    try:
        task = get_task(task_id)
        if task is None:
            resp = Result(message='Task not found', status_code=404)
            return resp.err_resp()

        if task.ready():
            resp = Result(
                detail=task.info.get('detail'),
                message=task.info.get('message', 'success'),
                status_code=task.info.get('status_code', 200),
                task={'taskId': task.id, 'status': task.status},
            )
        else:
            resp = Result(
                message=task.info.get('message', 'success'),
                status_code=task.info.get('status_code', 200),
                task={
                    'taskId': task.id,
                    'status': task.status,
                    'current': task.info.get('current', 0),
                    'total': task.info.get('total', 100),
                    'description': task.info.get('stage', ''),
                },
            )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=500,
            task={'taskId': task_id, 'status': 'ERROR'},
        )
        resp.err_resp()
