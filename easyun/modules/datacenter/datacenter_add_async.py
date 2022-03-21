# -*- coding: utf-8 -*-
"""
  @module:  DataCenter Creation
  @desc:    create some datacenter basic service, like vpc, subnet, securitygroup, etc.
  @auth:    aleck
"""

from flask import current_app,jsonify, request
from apiflask import Schema, input, output, doc, abort, auth_required
from apiflask.fields import Integer, String, List, Dict, DateTime, Boolean
from apiflask.validators import Length, OneOf
from celery.result import ResultBase, AsyncResult
from easyun import db, log, celery
from easyun.common.auth import auth_token
from easyun.common.models import Account
from easyun.common.result import Result
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
            status_code='2003'
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


'''
# celery create_dc_task log for reference:
2022-03-20 16:04:26,568 INFO sqlalchemy.engine.Engine [generated in 0.00023s] (4,)
[2022-03-20 16:04:26,568: INFO/ForkPoolWorker-1] [generated in 0.00023s] (4,)
[2022-03-20 16:04:26,569: INFO/ForkPoolWorker-1] [DataCenter]task11 metadata updated
[2022-03-20 16:04:26,719: INFO/ForkPoolWorker-1] [IGW]igw-0376b9c38949a266a created
[2022-03-20 16:04:26,919: INFO/ForkPoolWorker-1] [IGW]igw-0376b9c38949a266a attached to vpc-0d9a9d76df8e44a76
[2022-03-20 16:04:27,259: INFO/ForkPoolWorker-1] [Subnet]subnet-0fe28852000b1f828 created
[2022-03-20 16:04:27,502: INFO/ForkPoolWorker-1] [Subnet]subnet-0fc9ce4ca2a892874 created
[2022-03-20 16:04:27,774: WARNING/ForkPoolWorker-1] [{'Key': 'Flag', 'Value': 'task11'}, {'Key': 'Name', 'Value': 'task1-rtb-igw'}]
[2022-03-20 16:04:27,900: INFO/ForkPoolWorker-1] [RouteTable]0.0.0.0/0 created
[2022-03-20 16:04:28,654: INFO/ForkPoolWorker-1] [Subnet]subnet-03ac46ff89d2cff20 created
[2022-03-20 16:04:28,973: INFO/ForkPoolWorker-1] [Subnet]subnet-021a9864cd01c18ff created
[2022-03-20 16:04:29,228: INFO/ForkPoolWorker-1] [EIP]35.78.143.43 created
[2022-03-20 16:04:29,557: INFO/ForkPoolWorker-1] [NatGW]nat-0ef9d2d996a9aae79 creating
[2022-03-20 16:06:30,253: INFO/ForkPoolWorker-1] [NatGW]nat-0ef9d2d996a9aae79 created
[2022-03-20 16:06:30,694: INFO/ForkPoolWorker-1] [Route]0.0.0.0/0 created
[2022-03-20 16:06:31,975: INFO/ForkPoolWorker-1] [SecGroup]default updated
[2022-03-20 16:06:32,704: INFO/ForkPoolWorker-1] [SecGroup]task1-sg-webapp created
[2022-03-20 16:06:33,381: INFO/ForkPoolWorker-1] [SecGroup]task1-sg-webapp created
[2022-03-20 16:06:33,387: INFO/ForkPoolWorker-1] [DataCenter]task11 created successfully !
2022-03-20 16:06:33,397 INFO sqlalchemy.engine.Engine ROLLBACK
[2022-03-20 16:06:33,397: INFO/ForkPoolWorker-1] ROLLBACK
[2022-03-20 16:06:33,404: INFO/ForkPoolWorker-1] Task easyun.modules.datacenter.tasks_async.create_dc_task[78bc9f52-a8ef-41ad-8ace-0206ed33e4c5] succeeded in 128.12716651599476s: {'detail': <Datacenter 4>, 'status_code': 200}
'''

