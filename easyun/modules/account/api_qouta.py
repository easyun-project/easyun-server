# -*- coding: utf-8 -*-
"""
  @module:  Service Quotas
  @desc:    获取云账号下资源配额相关信息
"""

from easyun.common.auth import auth_token
from easyun.common.models import Datacenter
from easyun.common.schemas import MsgOut
from easyun.common.result import Result
from easyun.libs.utils import load_json_config
from easyun.cloud import get_account
from .schema import QuotaItem
from . import bp


@bp.get('/quota')
@bp.auth_required(auth_token)
@bp.output(QuotaItem(many=True))
def get_region_quota():
    '''获取指定region的资源配额'''
    from flask import request
    thisRegion = request.headers.get('X-Region')
    account = get_account()

    dcList = [dc.name for dc in Datacenter.query.filter_by(region=thisRegion)]
    serviceCodes = load_json_config('aws_quota_codes', 'easyun/cloud/aws/config')

    vpcQuotaCodes = [q['quotaCode'] for q in serviceCodes['vpcQuotaCodes']]
    networkQuotas = account.get_quotas('vpc', vpcQuotaCodes, region=thisRegion)
    eipQuota = account.get_quota('ec2', 'L-0263D0A3', region=thisRegion)
    networkQuotas.append(eipQuota)

    elbQuotaCodes = [q['quotaCode'] for q in serviceCodes['elbQuotaCodes']]
    elasticLBQuotas = account.get_quotas('elasticloadbalancing', elbQuotaCodes, region=thisRegion)

    ec2QuotaCodes = [q['quotaCode'] for q in serviceCodes['ec2QuotaCodes']]
    serverQuotas = account.get_quotas('elasticloadbalancing', ec2QuotaCodes, region=thisRegion)

    ebsQuotaCodes = [q['quotaCode'] for q in serviceCodes['ebsQuotaCodes']]
    volumeQuotas = account.get_quotas('ebs', ebsQuotaCodes, region=thisRegion)

    rdsQuotaCodes = [q['quotaCode'] for q in serviceCodes['rdsQuotaCodes']]
    databaseQuotas = account.get_quotas('rds', rdsQuotaCodes, region=thisRegion)

    quotaList = {
        'dcList': dcList,
        'networkQuotas': networkQuotas,
        'elasticLBQuotas': elasticLBQuotas,
        'serverQuotas': serverQuotas,
        'volumeQuotas': volumeQuotas,
        'databaseQuotas': databaseQuotas,
    }

    resp = Result(detail=quotaList, status_code=200)
    return resp.make_resp()


@bp.get('/quota/all')
@bp.auth_required(auth_token)
@bp.output(MsgOut)
def get_account_quota():
    '''获取云账号下资源配额【to-be-done】'''
    resp = Result(detail='功能开发中...', status_code=200)
    return resp.make_resp()
