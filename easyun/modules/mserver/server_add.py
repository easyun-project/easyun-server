# -*- coding: utf-8 -*-
'''
@Description: Server Management - Add new server
'''
from apiflask import Schema
from apiflask.fields import Integer, String, List, Dict
from apiflask.validators import Length
from easyun.common.auth import auth_token
from easyun.common.result import Result
from easyun.providers import get_datacenter
from .schemas import NewSvrItem
from . import bp


class SvrParmIn(Schema):
    dcName = String(required=True, metadata={"example": "Easyun"})
    tagName = String(required=True, validate=Length(0, 40), metadata={"example": "dev_server_1"})
    svrNumber = Integer(required=True, metadata={"example": 1})
    ImageId = String(required=True, metadata={"example": "ami-083654bd07b5da81d"})
    InstanceType = String(required=True, metadata={"example": "t3.nano"})
    SubnetId = String(required=True, metadata={"example": "subnet-06bfe659f6ecc2eed"})
    SecurityGroupIds = List(String(required=True, metadata={"example": "sg-05df5c8e8396d06e9"}))
    KeyName = String(required=True, metadata={"example": "key_easyun_dev"})
    BlockDeviceMappings = List(Dict(), required=True)


@bp.post('')
@bp.auth_required(auth_token)
@bp.input(SvrParmIn, arg_name='parm')
@bp.output(NewSvrItem(many=True))
def add_server(parm):
    '''新建云服务器(EC2)'''
    try:
        dc = get_datacenter(parm['dcName'])
        svrList = dc.resource.create_server(parm)
        resp = Result(detail=svrList, status_code=200)
        return resp.make_resp()
    except Exception as ex:
        response = Result(message='server creation failed', status_code=3001)
        return response.err_resp()
