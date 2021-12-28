# -*- coding: utf-8 -*-
"""dashboard model views."""

from apiflask import Schema, input, output, auth_required
from datetime import datetime
from apiflask.fields import String, List,Nested, Boolean, Date
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account


# 定义 aws info
class awsInfo(Schema):
    accountID = String()
    accountType = String()
    role = String()

class keypairList(Schema):
    keyName = String()
    pemUrl = String()

class freeTier(Schema):
    enRemind = Boolean()
    atvDate = Date()
    icoStatus = String()

class AccountInfoOut(Schema):
    awsInfo = Nested(awsInfo)
    freeTier = Nested(freeTier)
    keyList = List(Nested(keypairList))


@bp.get("/info")
@auth_required(auth_token)
@output(AccountInfoOut)
def account_info():
    '''获取Account 页面信息'''
    try:
        curr_account:Account = Account.query.first()
        awsInfo = {
            'accountID': curr_account.account_id,
            'accountType': curr_account.aws_type,
            'role': curr_account.role
        }

        now = datetime.now()
        freeTier = {
            'atvDate' : datetime.date(now),
            'icoStatus' : 'green',
            'enRemind' : True
        }

        keypairList = [
                {
                'keyName' : 'key_easyun_dev1',
                'pemUrl' : 'http://127.0.0.1:6660/download/keyname01',
                },
                {
                'keyName' : 'key_easyun_user1',
                'pemUrl' : 'http://127.0.0.1:6660/download/keyname02',
                },
                {
                'keyName' : 'key_easyun_user2',
                'pemUrl' : 'http://127.0.0.1:6660/download/keyname03',
                },
        ]

        AccountInfo = {
            'awsInfo' : awsInfo,
            'keyList' : keypairList,
            'freeTier' : freeTier
        }

        resp = Result(
            detail=AccountInfo
            )
        return resp.make_resp()
    except Exception as ex:
        resp = Result(message=str(ex), status_code=9001)
        return resp.make_resp()




class KeypairIn(Schema):
    keyName = String()


@bp.post("/add_key")
@auth_required(auth_token)
@input(KeypairIn)
def add_key(data):
    '''添加Keypair'''
    resp = Result(
        detail={
            'keyName' : data['keyName'],
            'pemUrl' : 'http://127.0.0.1:6660/download/'+data['keyName']
        }
    )
    return resp.make_resp()    