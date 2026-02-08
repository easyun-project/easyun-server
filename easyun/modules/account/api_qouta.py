# -*- coding: utf-8 -*-
"""
  @module:  Service Qoutas
  @desc:    获取云账号下资源配额相关信息
  @auth:    aleck
"""

from easyun.common.auth import auth_token
from easyun.common.models import Datacenter
from easyun.common.schemas import RegionCodeQuery
from easyun.common.result import Result
from easyun.libs.utils import load_json_config
from easyun.cloud.aws.sdk_quotas import ServiceQuotas
from . import bp


@bp.get('/quota')
@bp.auth_required(auth_token)
@bp.input(RegionCodeQuery, location='query', arg_name='parm')
def get_region_quota(parm):
    '''获取指定region的资源配额'''
    thisRegion = parm['region']
    sq = ServiceQuotas(thisRegion)

    dcList = [dc.name for dc in Datacenter.query.filter_by(region=thisRegion)]
    serviceCodes = load_json_config('aws_quota_codes')

    vpcQuotaCodes = [q['quotaCode'] for q in serviceCodes['vpcQuotaCodes']]
    networkQuotas = sq.get_service_quotas('vpc', vpcQuotaCodes)
    # eip 是个列外，单独获取后append上去
    eipQuota = sq.get_service_quota('ec2', 'L-0263D0A3')
    networkQuotas.append(eipQuota)

    elbQuotaCodes = [q['quotaCode'] for q in serviceCodes['elbQuotaCodes']]
    elasticLBQuotas = sq.get_service_quotas('elasticloadbalancing', elbQuotaCodes)

    ec2QuotaCodes = [q['quotaCode'] for q in serviceCodes['ec2QuotaCodes']]
    serverQuotas = sq.get_service_quotas('elasticloadbalancing', ec2QuotaCodes)

    ebsQuotaCodes = [q['quotaCode'] for q in serviceCodes['ebsQuotaCodes']]
    volumeQuotas = sq.get_service_quotas('ebs', ebsQuotaCodes)

    rdsQuotaCodes = [q['quotaCode'] for q in serviceCodes['rdsQuotaCodes']]
    databaseQuotas = sq.get_service_quotas('rds', rdsQuotaCodes)

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
def get_account_quota():
    '''获取云账号下资源配额【to-be-done】'''
    pass

    resp = Result(detail='功能开发中...', status_code=200)
    return resp.make_resp()
