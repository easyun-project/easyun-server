# -*- coding: utf-8 -*-
'''
@Description: server models
@LastEditors: aleck
'''

import math
from easyun import db
from apiflask.validators import Length, OneOf


'''预定义支持的OS列表'''
# 后续放在配置文件中便于维护
AMI_Win = [
    {
        'amiName': 'Windows_Server-2012-R2_RTM-English-64Bit-Base-2021.11.10',
        'imgName': 'Windows Server 2012 R2 64Bit',
        'imgCode': 'windows',
        'imgVersion': '2021.11.10'
    },
    {
        'amiName': 'Windows_Server-2016-English-Full-Base-2021.11.10',
        'imgName': 'Windows Server 2016',
        'imgCode': 'windows',
        'imgVersion': '2021.11.10'         
    },   
    {
        'amiName': 'Windows_Server-2019-English-Full-Base-2021.11.10',
        'imgName': 'Windows Server 2019',
        'imgCode': 'windows',
        'imgVersion': '2021.11.10'
    },
    {
        'amiName': 'Windows_Server-2022-English-Full-Base-2021.11.16',
        'imgName': 'Windows Server 2022',
        'imgCode': 'windows',
        'imgVersion': '2021.11.10'         
    }
]

AMI_Lnx = [
    {
        'amiName': 'amzn2-ami-kernel-5.10-hvm-2.0.20211201.0-x86_64-gp2',
        'imgName': 'Amazon Linux 2 Kernel 5.10',
        'imgCode': 'amzn2',
        'imgVersion': '2.0.20211201.0'
    },
    {
        'amiName': 'RHEL-8.4.0_HVM-20210504-x86_64-2-Hourly2-GP2',
        'imgName': 'Red Hat Enterprise Linux',
        'imgCode': 'rhel',
        'imgVersion': '8.4'     
    },   
    {
        'amiName': 'suse-sles-15-sp2-v20201211-hvm-ssd-x86_64',
        'imgName': 'SUSE Linux Enterprise Server',
        'imgCode': 'sles',
        'imgVersion': '15 SP2'      
    },
    {
        'amiName': 'suse-sles-12-sp5-v20201212-hvm-ssd-x86_64',
        'imgName': 'SUSE Linux Enterprise Server',
        'imgCode': 'sles',
        'imgVersion': '12 SP5'         
    },
    {
        'amiName': 'ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20211021',
        'imgName': 'Ubuntu',
        'imgCode': 'ubuntu',
        'imgVersion': '20.04 LTS'
    },
    {
        'amiName': 'ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20211027',
        'imgName': 'Ubuntu',
        'imgCode': 'ubuntu',
        'imgVersion': '18.04 LTS'       
    },   
    {
        'amiName': 'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20210928',
        'imgName': 'Ubuntu',
        'imgCode': 'ubuntu',
        'imgVersion': '16.04 LTS'
    },
    {
        'amiName': 'debian-10-amd64-20210208-542',
        'imgName': 'Debian 10',
        'imgCode': 'ubuntu',
        'imgVersion': '20210208'         
    } 
]


class server_ami:
    """
    Create a Server AMI list table
    """

    __tablename__ = 'server_ami'

    ami_id = db.Column(db.Integer, primary_key=True)    # "ImageId": "ami-00001ae98aac59c70",
    name = db.Column(db.String)     # "Name": "Windows_Server-2016-2021.08.11",
    platform = db.Column(db.String)     # "Platform": "windows",
    detail = db.Column(db.String)       # "PlatformDetails": "Windows with SQL Server Enterprise",
    osname = db.Column(db.String)    # "Description": "Microsoft Windows Server 2016 AMI provided by Amazon",
    osversion = db.Column(db.String)    # "2016",
    rootdev = db.Column(db.String)  # "RootDeviceName": "/dev/sda1",
    rootype = db.Column(db.String)  # "RootDeviceType": "ebs",
    

    def __init__(self, ami_id=None, name=None, platform=None, detail=None, osname=None, osversion=None):
        self.ami_id = ami_id
        self.name = name
        self.platform = platform
        self.detail = platform
        self.osname = osname
        self.osversion = osversion


    def foo(self):
        # do something
        
        return ''
