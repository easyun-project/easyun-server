# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Creation
  @desc:    create some datacenter basic service, like vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

import boto3
from apiflask import Schema, input, output, doc, abort, auth_required
from apiflask.fields import Integer, String, List, Dict, DateTime, Boolean
from apiflask.validators import Length, OneOf
from celery.result import ResultBase, AsyncResult
from easyun import db, log, celery
from easyun.common.auth import auth_token
from easyun.common.models import Account, Datacenter
from easyun.common.utils import len_iter
from easyun.common.result import Result
from easyun.cloud.aws_quota import get_quota_value
from .schemas import CreateDcParms, CreateDcResult, DcParmIn
from .tasks_async import create_dc_task
from . import bp, logger, DryRun


@bp.post('/add-async')
@auth_required(auth_token)
@input(CreateDcParms)
# @output(CreateDcResult)
@log.api_error(logger)
def create_dc_async(parm):
    '''创建 Datacenter 及基础资源[异步]'''
    try:
        # Check the prerequisites before create datacenter task
        dcName = parm['dcName']
        dcRgeion = parm['dcRegion']

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

    try:
        curr_user = auth_token.current_user.username
        task = create_dc_task.apply_async(args=[parm, curr_user])
        resp = Result(
            message='CREATING',
            status_code=200,
            task_id=task.id,
        )
        return resp.make_resp()

    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=2003
        )
        resp.err_resp()



class TaskIdQuery(Schema):
    id = String(required=True,   # celery task UUID
        validate=Length(0, 36),
        example="1603a978-e5a0-4e6a-b38c-4c751ff5fff8"
    )

@bp.get('/add-result')
@auth_required(auth_token)
@input(TaskIdQuery, location='query')
# @output(CreateDcResult)
def create_dc_result(parm):
    '''获取 add-task 任务执行结果'''
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
                task_id = task.id,
                http_status_code = task.info.get('http_status_code', 200)
            )
        # task.state: PENDING/STARTED/SUCCESS/FAILURE
        else:            
            # 通过task.info.get()获得 update_state() meta数据
            resp = Result(
                detail = {
                    'current': task.info.get('current', 0), # 当前循环进度
                    'total': task.info.get('total', 100), # 总循环进度
                },
                message = task.info.get('stage', ''),
                status_code = 200,
                task_id = task.id
            )
        return resp.make_resp()

    # 如查询过程出现了一些问题
    except Exception as ex:
        resp = Result(
            message=str(ex),
            status_code=task.info.get('status_code'),
            task_id = task.id
        )
        resp.err_resp()
