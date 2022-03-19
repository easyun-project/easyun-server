# -*- coding: utf-8 -*-
"""
  @module:  AWS ec2 instance types
  @desc:    Define basic attributes of AWS EC2 in this file.  
  @auth:    aleck
"""
from easyun.cloud.aws_price import get_attribute_values


'''全部受支持的Instance Tpye列表'''
ALL_InstanceType = get_attribute_values('AmazonEC2','instanceType')


'''EC2 Instance Family 列表'''
# 后续放在配置文件中便于维护
Instance_Family = [
    {
        'catgName': 'general',
        'catdesCode': 'GP',    # General Purpose
        'familyList': [
            {'familyName':'t2', 'familyDes':'突增实例', 'insArch':'x86_64'},
            {'familyName':'t3', 'familyDes':'突增实例', 'insArch':'x86_64'},
            {'familyName':'t3a', 'familyDes':'突增实例-AMD', 'insArch':'x86_64'},
            {'familyName':'m4', 'familyDes':'通用实例', 'insArch':'x86_64'},
            {'familyName':'m5', 'familyDes':'通用实例', 'insArch':'x86_64'},
            {'familyName':'m5d', 'familyDes':'通用实例', 'insArch':'x86_64'},
            {'familyName':'m5a', 'familyDes':'通用实例-AMD', 'insArch':'x86_64'},
            {'familyName':'m5ad', 'familyDes':'通用实例-AMD', 'insArch':'x86_64'},
            {'familyName':'m5n', 'familyDes':'通用实例', 'insArch':'x86_64'},
            {'familyName':'m5zn', 'familyDes':'通用实例', 'insArch':'x86_64'},
            {'familyName':'m6', 'familyDes':'通用实例', 'insArch':'x86_64'},
            {'familyName':'m6i', 'familyDes':'通用实例', 'insArch':'x86_64'},
            {'familyName':'m6a', 'familyDes':'通用实例-AMD', 'insArch':'x86_64'},
            {'familyName':'t4g', 'familyDes':'突增实例-ARM', 'insArch':'arm64'},
            {'familyName':'m6g', 'familyDes':'通用实例-ARM', 'insArch':'arm64'},
            {'familyName':'m6gd', 'familyDes':'通用实例-ARM', 'insArch':'arm64'},
            {'familyName':'a1', 'familyDes':'突增实例', 'insArch':'arm64'}
        ]
    },
    {
        'catgName': 'compute',
        'catdesCode': 'CO',    # Compute Optimized
        'familyList': [
            {'familyName':'c4', 'familyDes':'计算密集型', 'insArch':'x86_64'},
            {'familyName':'c5', 'familyDes':'计算密集型', 'insArch':'x86_64'},
            {'familyName':'c5a', 'familyDes':'计算密集型-AMD', 'insArch':'x86_64'},
            {'familyName':'c5d', 'familyDes':'计算密集型-AMD', 'insArch':'x86_64'},
            {'familyName':'c5ad', 'familyDes':'计算密集型-AMD', 'insArch':'x86_64'},
            {'familyName':'c5n', 'familyDes':'计算密集型-AMD', 'insArch':'x86_64'},
            {'familyName':'c6i', 'familyDes':'计算密集型', 'insArch':'x86_64'},
            {'familyName':'c6g', 'familyDes':'计算密集型-ARM', 'insArch':'arm64'},
            {'familyName':'c6gn', 'familyDes':'计算密集型-ARM', 'insArch':'arm64'},
            {'familyName':'c6gd', 'familyDes':'计算密集型-ARM', 'insArch':'arm64'},            
            {'familyName':'c7g', 'familyDes':'计算密集型-ARM', 'insArch':'arm64'}
        ]
    },
    {
        'catgName': 'memory',
        'catdesCode': 'MO',    # Memory Optimized
        'familyList': [
            {'familyName':'r4', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'r5', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'r5d', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'r5a', 'familyDes':'内存优化实例-AMD', 'insArch':'x86_64'},
            {'familyName':'r5ad', 'familyDes':'内存优化实例-AMD', 'insArch':'x86_64'},
            {'familyName':'r5b', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'r5n', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'r5dn', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'r6i', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'r6g', 'familyDes':'内存优化实例-ARM', 'insArch':'arm64'},
            {'familyName':'r6gd', 'familyDes':'内存优化实例-ARM', 'insArch':'arm64'},  
            {'familyName':'x1', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'x1e', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'z1d', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'x2idn', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'x2iedn', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'x2iezn', 'familyDes':'内存优化实例', 'insArch':'x86_64'},
            {'familyName':'x2gd', 'familyDes':'内存优化实例-ARM', 'insArch':'arm64'},
            {'familyName':'x2g', 'familyDes':'内存优化实例-ARM', 'insArch':'arm64'}
        ]
    },
    {
        'catgName': 'storage',
        'catdesCode': 'SO',    # Storage Optimized
        'familyList': [
            {'familyName':'d2', 'familyDes':'存储实例-HDD', 'insArch':'x86_64'},
            {'familyName':'d3', 'familyDes':'存储实例-HDD', 'insArch':'x86_64'},
            {'familyName':'d3en', 'familyDes':'存储实例-HDD', 'insArch':'x86_64'},
            {'familyName':'i3', 'familyDes':'存储实例-NVMe', 'insArch':'x86_64'},
            {'familyName':'i3en', 'familyDes':'存储实例-NVMe', 'insArch':'x86_64'},
            {'familyName':'i4i', 'familyDes':'存储优化-Nitro SSD', 'insArch':'x86_64'},
            {'familyName':'is4gen', 'familyDes':'存储优化-Nitro SSD', 'insArch':'x86_64'},
            {'familyName':'im4gn', 'familyDes':'存储优化-Nitro SSD', 'insArch':'x86_64'},
            {'familyName':'h1', 'familyDes':'存储实例-HDD', 'insArch':'x86_64'}
        ]
    },
    {
        'catgName': 'accelerate',
        'catdesCode': 'AC',    # Accelerated Computing
        'familyList': [
            {'familyName':'p2', 'familyDes':'GPU实例-K80', 'insArch':'x86_64'},
            {'familyName':'p3', 'familyDes':'GPU实例-V100', 'insArch':'x86_64'},
            {'familyName':'p4', 'familyDes':'GPU实例-A100', 'insArch':'x86_64'},
            {'familyName':'p4d', 'familyDes':'GPU实例-A100', 'insArch':'x86_64'},
            {'familyName':'dl1', 'familyDes':'ML训练-Gaudi', 'insArch':'x86_64'},
            {'familyName':'inf1', 'familyDes':'ML推理-Inferentia', 'insArch':'x86_64'},
            {'familyName':'g3', 'familyDes':'通用实例AMD', 'insArch':'x86_64'},
            {'familyName':'g4dn', 'familyDes':'GPU实例-T4', 'insArch':'x86_64'},
            {'familyName':'g4ad', 'familyDes':'GPU实例-Radeon', 'insArch':'x86_64'},
            {'familyName':'g5', 'familyDes':'GPU实例-A10G', 'insArch':'x86_64'},
            {'familyName':'g5g', 'familyDes':'GPU实例-T4G', 'insArch':'arm64'},
            {'familyName':'f1', 'familyDes':'加速计算实例-FPGA', 'insArch':'x86_64'},
            {'familyName':'vt1', 'familyDes':'视频转码实例', 'insArch':'x86_64'}
        ]
    }
]

def get_familyDes(parm):
    '''获取Instance Family描述信息'''
    for i in Instance_Family:        
        familyDes = [f['familyDes'] for f in i['familyList'] if f.get('familyName')==parm]
        if familyDes:
            return familyDes[0]
    if not familyDes:
        return parm+' Instance'
