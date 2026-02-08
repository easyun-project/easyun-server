# -*- coding: utf-8 -*-
"""
  @module:  Account Reminder
  @desc:    云账号日期提醒相关功能
  @auth:
"""

from easyun import db
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.models import Account
from easyun.cloud.account import get_cloud_account
from .schema import FreeTierQuery, FreeTierInfo, FreeTierParm
from . import bp


@bp.get('/reminder/freetier')
@bp.auth_required(auth_token)
@bp.input(FreeTierQuery, location='query', arg_name='parm')
@bp.output(FreeTierInfo, description='Get FreeTier Reminder Info')
def get_freetier_reminder(parm):
    '''获取云账号的FreeTier 提醒'''
    accountId = parm.get('account_id')
    try:
        account = Account.query.first()
        if account.remind:
            remainDays = 365 - account.get_days()
            if remainDays < 30:
                iconColor = 'red'
            elif remainDays < 90:
                iconColor = 'yellow'
            else:
                iconColor = 'green'
            remindInfo = {
                'isReminderOn': account.remind,
                'activeDate': account.active_date,
                'remainDays': remainDays,
                'iconColor': iconColor
            }
        else:
            remindInfo = {
                'isReminderOn': account.remind
            }
        resp = Result(detail=remindInfo, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2012)
        response.err_resp()


@bp.put('/reminder/freetier')
@bp.auth_required(auth_token)
@bp.input(FreeTierParm, arg_name='parms')
# @bp.output(FreeTierInfo, description='Get FreeTier Reminder Info')
def set_freetier_reminder(parms):
    '''修改云账号的FreeTier 提醒'''
    accountId = parms.get('accountId')
    isReminderOn = parms['isReminderOn']
    activeDate = parms['activeDate']
    try:
        # 增加判断:如果activeDate在一年前,则不支持启用
        account = Account.query.first()
        if isReminderOn:
            newDict = {
                'remind': isReminderOn,
                'active_date': activeDate
            }
            account.update_dict(newDict)
        elif not isReminderOn:
            account.disable_remind()
        else:
            pass
        db.session.commit()
        # cAccount = get_cloud_account(accountId)
        # remindInfo = cAccount.get_freetier_reminder()
        remindInfo = {
            'isReminderOn': account.remind,
            'activeDate': account.active_date,
            'remainDays': 365 - account.get_days()
        }
        resp = Result(detail=remindInfo, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2013)
        response.err_resp()


@bp.get('/reminder/credit')
@bp.auth_required(auth_token)
@bp.input(FreeTierQuery, location='query', arg_name='parm')
def get_credit_reminder(parm):
    '''获取云账号的Credits提醒【to-be-done】'''
    accountId = parm.get('account_id')
    try:
        account = get_cloud_account(accountId)
        remindInfo = account.get_credit_reminder()
        resp = Result(detail=remindInfo, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2022)
        response.err_resp()


@bp.put('/reminder/credit')
@bp.auth_required(auth_token)
@bp.input(FreeTierParm, location='query', arg_name='parms')
def set_credit_reminder(parms):
    '''设置云账号的Credits提醒【to-be-done】'''
    accountId = parms.get('accountId')
    isReminderOn = parms['isReminderOn']
    activeDate = parms['activeDate']
    try:
        account = get_cloud_account(accountId)
        remindInfo = account.set_credit_reminder(isReminderOn, 500, activeDate)
        resp = Result(detail=remindInfo, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message=str(ex), status_code=2023)
        response.err_resp()
