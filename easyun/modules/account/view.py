# -*- coding: utf-8 -*-
"""dashboard model views."""
from apiflask import auth_required, Schema
from apiflask.decorators import output
from apiflask.fields import String
from easyun.common.result import Result
from . import bp
from easyun.common.auth import auth_token
from easyun.common.models import Account

class AWSInfoOutSchema(Schema):
    account_id = String()

@auth_required(auth_token)
@bp.get("/aws_info")
@output(AWSInfoOutSchema)
def aws_info():
    try:
        account:Account = Account.query.first()
        res = Result(detail=account)
        return res.make_resp()
    except Exception as e:
        res = Result(message=str(e), status_code=2001)
        res.err_resp()


@bp.get("/test-cicd")
def test():
    try:
        return "ok-cicd"
        account:Account = Account.query.first()
        res = Result(detail=account)
        return res.make_resp()
    except Exception as e:
        res = Result(message=str(e), status_code=2001)
        res.err_resp()