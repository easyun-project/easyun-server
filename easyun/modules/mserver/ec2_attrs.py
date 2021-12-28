# -*- coding: utf-8 -*-
'''
@Description: server models
@LastEditors: aleck
'''

import boto3


'''预定义支持的AMI列表'''
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
        'imgCode': 'debian',
        'imgVersion': '20210208'         
    } 
]


'''支持的Instance Tpyes列表'''
# 后续放在配置文件中便于维护
Instance_Types = [
    {
        'useCases': 'general',
        'desCode': 'GP',    # General Purpose
        'insFamily': ['t2', 't3', 't3a', 'm4', 'm5', 'm5a', 'm6', 'm6a', 't4g', 'm6g', 'a1']
    }, 
    {
        'useCases': 'compute',
        'desCode': 'CO',    # Compute Optimized
        'insFamily': ['c4', 'c5', 'c5a', 'c6i', 'c6g', 'c7g']
    }, 
    {
        'useCases': 'memory',
        'desCode': 'MO',    # Memory Optimized
        'insFamily': ['r4', 'r5', 'r5a', 'r5b', 'r5n', 'r5dn', 'r6i', 'x1', 'z1d', 'x2idn', 'x2iedn', 'x2iezn', 'R6g','X2g']
    }, 
    {
        'useCases': 'storage',
        'desCode': 'SO',    # Storage Optimized
        'insFamily': ['d2', 'd3', 'd3en', 'i3', 'i3en', 'i4i', 'Is4gen', 'Im4gn', 'h1']
    },    
    {
        'useCases': 'accelerate',
        'desCode': 'AC',    # Accelerated Computing
        'insFamily': ['p2', 'p3', 'p4', 'dl1', 'inf1', 'g3', 'g4dn', 'g4ad', 'g5', 'g5g', 'f1', 'vt1']
    }
]

'''支持的Instance OS列表'''
client_price = boto3.client('pricing')
response = client_price.get_attribute_values(
    ServiceCode='AmazonEC2',
    AttributeName='operatingSystem'
)
os_values = response['AttributeValues']
Instance_OS = [os['Value'] for os in os_values]
