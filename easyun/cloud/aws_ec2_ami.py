# -*- coding: utf-8 -*-
"""
  @module:  AWS ec2 images
  @desc:    Define basic attributes of AWS EC2 in this file.  
  @auth:    aleck
"""

import boto3


'''预定义支持的AMI列表'''
# 后续放在配置文件中便于维护
AMI_Win = {
    'x86_64': [
        {
            'amiName': 'Windows_Server-2012-R2_RTM-English-64Bit-Base-2021.11.10',
            'osName': 'Windows Server 2012 R2 64Bit',
            'osCode': 'windows',
            'osVersion': '2021.11.10'
        },
        {
            'amiName': 'Windows_Server-2016-English-Full-Base-2021.11.10',
            'osName': 'Windows Server 2016',
            'osCode': 'windows',
            'osVersion': '2021.11.10'         
        },   
        {
            'amiName': 'Windows_Server-2019-English-Full-Base-2021.11.10',
            'osName': 'Windows Server 2019',
            'osCode': 'windows',
            'osVersion': '2021.11.10'
        },
        {
            'amiName': 'Windows_Server-2022-English-Full-Base-2021.11.16',
            'osName': 'Windows Server 2022',
            'osCode': 'windows',
            'osVersion': '2021.11.10'         
        }
    ],
    'arm64': [
        # Windows Server 暂无 arm 版本
    ]
}

AMI_Lnx = {
    'x86_64': [
        {
            'amiName': 'amzn2-ami-kernel-5.10-hvm-2.0.20211201.0-x86_64-gp2',
            'osName': 'Amazon Linux 2 Kernel 5.10',
            'osCode': 'amzn2',
            'osVersion': '2.0.20211201.0'
        },
        {
            'amiName': 'RHEL-8.4.0_HVM-20210504-x86_64-2-Hourly2-GP2',
            'osName': 'Red Hat Enterprise Linux',
            'osCode': 'rhel',
            'osVersion': '8.4'     
        },   
        {
            'amiName': 'suse-sles-15-sp2-v20201211-hvm-ssd-x86_64',
            'osName': 'SUSE Linux Enterprise Server',
            'osCode': 'sles',
            'osVersion': '15 SP2'      
        },
        {
            'amiName': 'suse-sles-12-sp5-v20201212-hvm-ssd-x86_64',
            'osName': 'SUSE Linux Enterprise Server',
            'osCode': 'sles',
            'osVersion': '12 SP5'         
        },
        {
            'amiName': 'ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20211021',
            'osName': 'Ubuntu',
            'osCode': 'ubuntu',
            'osVersion': '20.04 LTS'
        },
        {
            'amiName': 'ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20211027',
            'osName': 'Ubuntu',
            'osCode': 'ubuntu',
            'osVersion': '18.04 LTS'       
        },   
        {
            'amiName': 'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20210928',
            'osName': 'Ubuntu',
            'osCode': 'ubuntu',
            'osVersion': '16.04 LTS'
        },
        {
            'amiName': 'debian-10-amd64-20211011-792',
            'osName': 'Debian 10',
            'osCode': 'debian',
            'osVersion': '10 [2021.10]'
        }
    ],
    'arm64': [
        {
            'amiName': 'amzn2-ami-kernel-5.10-hvm-2.0.20211223.0-arm64-gp2',
            'osName': 'Amazon Linux 2 Kernel 5.10',
            'osCode': 'amzn2',
            'osVersion': '2.0.20211201.0'
        },
        {
            'amiName': 'RHEL-8.4.0_HVM-20210825-arm64-0-Hourly2-GP2',
            'osName': 'Red Hat Enterprise Linux',
            'osCode': 'rhel',
            'osVersion': '8.4'     
        },   
        {
            'amiName': 'suse-sles-15-sp2-v20210604-hvm-ssd-arm64',
            'osName': 'SUSE Linux Enterprise Server',
            'osCode': 'sles',
            'osVersion': '15 SP2'      
        },
        {
            'amiName': 'ubuntu/images/hvm-ssd/ubuntu-focal-20.04-arm64-server-20211129',
            'osName': 'Ubuntu',
            'osCode': 'ubuntu',
            'osVersion': '20.04 LTS'
        },
        {
            'amiName': 'ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-arm64-server-20211129',
            'osName': 'Ubuntu',
            'osCode': 'ubuntu',
            'osVersion': '18.04 LTS'       
        },   
        {
            'amiName': 'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-arm64-server-20210928',
            'osName': 'Ubuntu',
            'osCode': 'ubuntu',
            'osVersion': '16.04 LTS'
        },
        {
            'amiName': 'debian-10-arm64-20211011-792',
            'osName': 'Debian 10',
            'osCode': 'debian',
            'osVersion': '10 [2021.10]'
        }
    ]
}



'''支持的Instance OS列表'''
# AWS Price API only support us-east-1, ap-south-1
priceRegion = 'us-east-1'
try:
    client_price = boto3.client('pricing', region_name= priceRegion )
    response = client_price.get_attribute_values(
        ServiceCode='AmazonEC2',
        AttributeName='operatingSystem'
    )
    os_values = response['AttributeValues']
    Instance_OS = [os['Value'] for os in os_values]
except Exception:
    pass