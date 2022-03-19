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
from easyun.common.result import Result, make_resp, error_resp, bad_request
from .schemas import CreateDcParms, CreateDcResult, DcParmIn
from .tasks_dc import create_dc_task
from . import bp, logger, DryRun


@bp.post('/add-task')
@auth_required(auth_token)
@input(CreateDcParms)
@output(CreateDcResult)
@log.api_error(logger)
def create_dc_async(parm):
    '''创建 Datacenter 及基础资源[异步]'''
    task = create_dc_task.apply_async(args=[parm, ])
    # task = create_dc_task.delay([parm])
    resp = Result(
        task_id=task.id,
        status_code=200
    )
    return resp.make_resp()


@bp.get('/add-result/<task_id>')
@auth_required(auth_token)
# @output(CreateDcResult)
def fetch_task_result(task_id):
    '''获取 add-task 任务执行结果'''
    # task_id is celery task UUID
    # for example: '1603a978-e5a0-4e6a-b38c-4c751ff5fff8'
    try:
        task = create_dc_task.AsyncResult(task_id)
        if task.ready():
            taskRes = task.result
            resp = Result(
                detail=taskRes.get('detail'),
                message=taskRes.get('message'),
                status_code=taskRes.get('status_code')
            )
        elif task.state == 'PENDING': # 在等待
            resp = Result(
                detail={
                    'current': 0,
                    'total': 1,                
                },
                message=task.state,
            )
        elif task.state != 'FAILURE': # 没有失败
            resp = Result(
                # 通过task.info.get()获得 update_state() meta中的数据
                detail={
                    'current': task.info.get('current', 0), # 当前循环进度
                    'total': task.info.get('total', 1), # 总循环进度               
                },
                message=task.state,
            )
    # 如查询过程出现了一些问题
    except Exception as ex:
        resp = Result(
            detail={
                'current': 1,
                'total': 1,                
            },
            message=str(ex),
            status_code='2002'
        )        
        resp.err_resp()
