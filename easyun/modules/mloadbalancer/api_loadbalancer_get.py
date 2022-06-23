# encoding: utf-8
"""
  @module:  Load Banalancer Module
  @desc:    负载均衡器(ELB) 查询相关
  @auth:    aleck
"""

from apiflask import auth_required
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.common.schemas import DcNameQuery
from easyun.cloud.aws import get_datacenter
from easyun.cloud.aws.workload import get_load_balancer
# from .schemas import ElbModel, ElbBasic, ElbDetail
from . import bp


@bp.get('')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @bp.output(ElbModel(many=True), description='All Elb list (detail)')
def list_elb_detail(parm):
    '''获取数据中心全部负载均衡器信息'''
    dcName = parm.get('dc')
    try:
        dc = get_datacenter(dcName)
        elbList = dc.resources.list_all_loadbalancer()

        resp = Result(detail=elbList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=4601)
        return resp.err_resp()


@bp.get('/list')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @bp.output(ElbBasic(many=True), description='All Elb list (brief)')
def list_elb_brief(parm):
    '''获取数据中心全部负载均衡器列表[仅基础字段]'''
    dcName = parm.get('dc')
    try:
        dc = get_datacenter(dcName)
        elbList = dc.resources.get_loadbalancer_list()

        resp = Result(detail=elbList, status_code=200)
        return resp.make_resp()

    except Exception as ex:
        resp = Result(message=str(ex), status_code=4602)
        return resp.err_resp()


@bp.get('/<elb_id>')
@auth_required(auth_token)
@bp.input(DcNameQuery, location='query')
# @bp.output(ElbDetail, description='A Elb Detail Info')
def get_elb_detail(elb_id, parm):
    '''获取指定负载均衡器(Elb)详细信息【to-be-done】'''
    dcName = parm.get('dc')
    # 设置 boto3 接口默认 region_name
    # dcRegion = set_boto3_region(dcName)
    try:
        elb = get_load_balancer(elb_id, dcName)
        elbDetail = elb.get_detail()

        response = Result(detail=elbDetail, status_code=200)
        return response.make_resp()

    except Exception as ex:
        response = Result(message=str(ex), status_code=4603)
        response.err_resp()
