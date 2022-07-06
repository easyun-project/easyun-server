# -*- coding: utf-8 -*-
"""
  @module:  Cloud Account SDK Module
  @desc:    AWS SDK Boto3 Client and Resource Wrapper.
  @auth:
"""

from botocore.exceptions import ClientError
from easyun.common.models import Account
from easyun import db
# from ..session import get_easyun_session


_CLOUD_ACCOUNT = None


def get_cloud_account(account_id=None):
    global _CLOUD_ACCOUNT
    if _CLOUD_ACCOUNT is not None and _CLOUD_ACCOUNT.id == account_id:
        return _CLOUD_ACCOUNT
    else:
        if account_id is None:
            defAccount = Account.query.first()
            account_id = defAccount.account_id
        return CloudAccount(account_id)


class CloudAccount(object):
    # 【fix-me】
    def __init__(self, account_id):
        # self.session = get_easyun_session()
        self.id = account_id
        self.db = Account.query.filter_by(account_id=account_id).first()

    def get_basic(self):
        '''获取账号基本信息'''
        account = self.db
        try:
            basicDict = {
                'accountId': account.account_id,
                'accountType': account.aws_type,
                'role': account.role,
                'deployRegion': account.get_region(),
            },
            return basicDict
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_freetier_reminder(self):
        try:
            remainDays = 365 - self.db.get_days()
            if remainDays < 30:
                iconColor = 'red'
            elif remainDays < 90:
                iconColor = 'yellow'
            else:
                iconColor = 'green'
            remdDict = {
                'isReminderOn': self.db.remind,
                'activeDate': self.db.active_date,
                'remainDays': remainDays,
                'iconColor': iconColor
            }
            return remdDict
        except Exception as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def set_freetier_reminder(self, is_on: bool, date=None):
        try:
            if is_on:
                newDict = {
                    'remind': is_on,
                    'active_date': date
                }
                self.db.update_dict(newDict)
            elif not is_on:
                self.db.disable_remind()
            else:
                pass
            db.session.commit()
            return self.get_freetier_reminder()
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def get_credit_reminder(self):
        try:
            pass
            return
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))

    def set_credit_reminder(self, is_on: bool, amount=None, date=None):
        try:
            if is_on:
                pass
            else:
                pass
            return
        except ClientError as ex:
            return '%s: %s' % (self.__class__.__name__, str(ex))
