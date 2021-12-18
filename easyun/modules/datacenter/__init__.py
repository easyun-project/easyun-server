# -*- coding: utf-8 -*-
"""
  @file:    _init_.py
  @desc:    DataCenter Init module
"""

from apiflask import APIBlueprint
from easyun import FLAG
from easyun.common.models import Account

# define api version
ver = '/api/v1'

bp = APIBlueprint('数据中心管理', __name__, url_prefix = ver+'/datacenter') 

#单数据中心模式下，名称默认：Easyun
#tag:FLAG = DC_NAME,
DC_NAME = "Easyun"
#单数据中心模式下，DC Region 同 Deployed Region
DC_REGION = 'us-east-1'
# this_account = Account.query.filter_by(id=1).first()
# DC_REGION = this_account.get_region()

TagEasyun= [{
        'Key': 'Flag', 
        #单数据中心版本，DC名称默认Easyun
        'Value': FLAG   
        }]


VERBOSE = 1
DryRun=False

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


keypair_name = 'key_easyun_user'
keypair_filename = keypair_name+'.pem'


from . import datacenter_parm, datacenter_add, datacenter_get, datacenter_sdk, datacenter_delete 
