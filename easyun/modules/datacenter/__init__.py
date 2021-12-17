# -*- coding: utf-8 -*-
"""
  @author:  pengchang
  @license: (C) Copyright 2021, Node Supply Chain Manager Corporation Limited. 
  @file:    _init_.py
  @desc:    The DataCenter Init module
"""

from apiflask import APIBlueprint
from easyun.common.models import Account

# define api version
ver = '/api/v1'

bp = APIBlueprint('数据中心管理', __name__, url_prefix = ver+'/datacenter') 

REGION = "us-east-1"
# dc = Datacenter.query.filter_by(name="Easyun").first()
# REGION = dc.get_region()
FLAG = "Easyun"
VERBOSE = 1


secure_group1 = 'easyun-sg-default'
secure_group2 = 'easyun-sg-webapp'
secure_group3 = 'easyun-sg-database'
sg_list= ['easyun-sg-default','easyun-sg-webapp','easyun-sg-database']
sg_dict={'easyun-sg-default' : 'Secure Group For Easyun Default',
'easyun-sg-webapp' : 'Secure Group For Easyun Webapp',
'easyun-sg-database' :  'Secure Group For Easyun Database'
}


IpPermissions1=[{
        'IpProtocol': 'tcp',
        'FromPort': 3389,
        'ToPort': 3389,
        'IpRanges': [{
            'CidrIp': '0.0.0.0/0'
        }]
    }, {
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22,
        'IpRanges': [{
            'CidrIp': '0.0.0.0/0'
        }]
    }, {
        'IpProtocol': 'icmp',
        'FromPort': -1,
        'ToPort': -1,
        'IpRanges': [{
            'CidrIp': '0.0.0.0/0'
        }]
    }]

IpPermissions2=[{
    'IpProtocol': 'tcp',
    'FromPort': 22,
    'ToPort': 80,
    'IpRanges': [{
        'CidrIp': '0.0.0.0/0'
    }]
}, {
    'IpProtocol': 'tcp',
    'FromPort': 22,
    'ToPort': 443,
    'IpRanges': [{
        'CidrIp': '0.0.0.0/0'
    }]
}]
IpPermissions3=[{
    'IpProtocol': 'tcp',
    'FromPort': 22,
    'ToPort': 3306,
    'IpRanges': [{
        'CidrIp': '0.0.0.0/0'
    }]
}, {
    'IpProtocol': 'tcp',
    'FromPort': 22,
    'ToPort': 5432,
    'IpRanges': [{
        'CidrIp': '0.0.0.0/0'
    }]
},{
    'IpProtocol': 'tcp',
    'FromPort': 22,
    'ToPort': 1521,
    'IpRanges': [{
        'CidrIp': '0.0.0.0/0'
    }]
}, {
    'IpProtocol': 'tcp',
    'FromPort': 22,
    'ToPort': 1443,
    'IpRanges': [{
        'CidrIp': '0.0.0.0/0'
    }]
}]

sg_ip_dict={'easyun-sg-default' : IpPermissions1,
'easyun-sg-webapp' : IpPermissions2,
'easyun-sg-database' :  IpPermissions3
}

TagEasyun= [{
        'Key':
        'Flag',
        'Value':
        FLAG
        }]

keypair_name = 'key-easyun-user'
keypair_filename = 'key-easyun-user.pem'
from . import datacenter_add, datacenter_default, datacenter_get, datacenter_sdk, datacenter_delete
