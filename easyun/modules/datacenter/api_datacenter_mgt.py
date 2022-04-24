# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Creation
  @desc:    create some datacenter basic service, like vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

import boto3
from apiflask import Schema, input, output, auth_required
from apiflask.fields import String
from apiflask.validators import Length, OneOf
from celery.result import ResultBase, AsyncResult
from easyun import db, log, celery
from easyun.common.result import Result
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.schemas import DcNameParm
from easyun.libs.utils import len_iter
from easyun.cloud.aws_quota import get_quota_value
from easyun.cloud.utils import set_boto3_region
from easyun.cloud.sdk_tagging import RgTagging
from .schemas import CreateDcParms, CreateDcResult, DcParmIn
from .task_create import create_dc_task
from .task_delete import delete_dc_task
from . import bp, logger


@bp.post('')
@auth_required(auth_token)
@bp.input(CreateDcParms)
# @output(CreateDcResult)
@log.api_error(logger)
def create_dc_async(parm):
    '''创建 Datacenter 及基础资源[异步]'''
    dcName = parm['dcName']
    dcRgeion = parm['dcRegion']

    # Check the prerequisites before create datacenter task
    try:
        boto3.setup_default_session(region_name = dcRgeion ) 
        resource_ec2 = boto3.resource('ec2')

        # Check if the DC Name is available
        thisDC:Datacenter = Datacenter.query.filter_by(name = dcName).first()
        if (thisDC is not None):
            raise ValueError('DataCenter name already existed')
        # Check if VPC quota is enough
        vpcQuota = get_quota_value('vpc','L-F678F1CE')
        vpcIter = resource_ec2.vpcs.all()
        if len_iter(vpcIter)  >= int(vpcQuota):
            raise ValueError('The VPCs per Region limit has been reached')
        # Check if EIP quota is enough
        eipQuota = get_quota_value('ec2','L-0263D0A3')
        eipIter = resource_ec2.vpc_addresses.all()
        if len_iter(eipIter) >= int(eipQuota):
            raise ValueError('The EC2-VPC Elastic IPs limit has been reached')
 
    except Exception as ex:
        logger.error('[DataCenter]'+str(ex))
        resp = Result(
            message=str(ex),
            status_code= 2001
        )
        resp.err_resp()

    # create a datacenter creation async task
    try:
        currUser = auth_token.current_user.username
        task = create_dc_task.apply_async(args=[parm, currUser])
        resp = Result(
            task={
                'taskId':task.id,
                'description':'CREATING',
            },
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=2003
        )
        resp.err_resp()



@bp.delete('')
@auth_required(auth_token)
@bp.input(DcNameParm)
# @output(CreateDcResult)
@log.api_error(logger)
def delete_dc_async(parm):
    '''删除 Datacenter 及基础资源[异步]'''
    dcName = parm['dcName']
    dcRegion = set_boto3_region(dcName)
    # Check the prerequisites before create datacenter task
    try:        
        rgt = RgTagging( dcName )

        # step 1: DC resource empty checking - instance
        serverNum = rgt.sum_resources('ec2:instance')
        if serverNum > 0:
            raise ValueError(f'DataCenter NOT Empty, contains {serverNum} Server(s) resources.')

        # step 2: DC resource empty checking - volume
        volumeNum = rgt.sum_resources('ec2:volume')
        if volumeNum > 0:
            raise ValueError(f'DataCenter NOT Empty, contains {volumeNum} Volume(s) resources.')

        # step 3: DC resource empty checking - rds
        rdsNum =  rgt.sum_resources('rds:db')
        if rdsNum > 0:
            raise ValueError(f'DataCenter NOT Empty, contains {rdsNum} Database(s) resources.')

        # step 4: DC resource empty checking - NAT Gateway
        natgwNum =  rgt.sum_resources('ec2:natgateway')
        if natgwNum > 0:
            raise ValueError(f'DataCenter NOT Empty, contains {natgwNum} NatGateway(s) resources.')

    except Exception as ex:
        logger.error('[DataCenter]'+str(ex))
        resp = Result(
            message=str(ex),
            status_code= 2011
        )
        resp.err_resp()
            
    # create a datacenter delete async task
    try:
        # currUser = auth_token.current_user.username
        task = delete_dc_task.apply_async(args=[parm, dcRegion])
        resp = Result(
            task={
                'taskId':task.id,
                'description':'DELETING',
            },
            status_code=200
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=2013
        )
        resp.err_resp()


class TaskIdQuery(Schema):
    id = String(required=True,   # celery task UUID
        validate=Length(0, 36),
        example="1603a978-e5a0-4e6a-b38c-4c751ff5fff8"
    )

@bp.get('/task')
@auth_required(auth_token)
@input(TaskIdQuery, location='query')
# @output(CreateDcResult)
def get_task_result(parm):
    '''获取异步任务执行结果'''
    try:
        # task = AsyncResult(parm['id'], app=celery)
        task:AsyncResult = create_dc_task.AsyncResult(parm['id'])
        # .ready() Return `True` if the task has executed.
        if task.ready(): 
            # 通过task.info 获得 task return 数据
            resp = Result(
                detail = task.info.get('detail'),
                message = task.info.get('message', 'success'),
                status_code = task.info.get('status_code', 200),
                task = { 'taskId':task.id },
                http_status_code = task.info.get('http_status_code', 200)
            )
        # task.state: PENDING/STARTED/SUCCESS/FAILURE
        else:            
            # 通过task.info.get()获得 update_state() meta数据
            resp = Result(
                # detail = {}, # 任务执行的最终结果
                message = task.info.get('message', 'success'),
                status_code = 200,
                task = {
                    'taskId':task.id,
                    'current': task.info.get('current', 0), # 当前循环进度
                    'total': task.info.get('total', 100), # 总循环进度
                    'description': task.info.get('stage', ''), # 阶段描述                    
                }
            )
        return resp.make_resp()

    # 如查询过程出现了一些问题
    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=task.info.get('status_code'),
            task = {'taskId':task.id}
        )
        resp.err_resp()
