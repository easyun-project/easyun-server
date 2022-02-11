# -*- coding: utf-8 -*-
"""
  @module:  AWS ec2 instance types
  @desc:    Define basic attributes of AWS EC2 in this file.  
  @auth:    aleck
"""

import boto3


'''支持的Instance Tpyes列表'''
# 临时使用，后续可删除
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


'''EC2 Instance Family 列表'''
# 后续放在配置文件中便于维护
Instance_Family = [
    {
        'insCatg': 'general',
        'desCode': 'GP',    # General Purpose
        'insFamily': [
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
        'insCatg': 'compute',
        'desCode': 'CO',    # Compute Optimized
        'insFamily': [
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
        'insCatg': 'memory',
        'desCode': 'MO',    # Memory Optimized
        'insFamily': [
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
        'insCatg': 'storage',
        'desCode': 'SO',    # Storage Optimized
        'insFamily': [
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
        'insCatg': 'accelerate',
        'desCode': 'AC',    # Accelerated Computing
        'insFamily': [
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
        familyDes = [f['familyDes'] for f in i['insFamily'] if f.get('familyName')==parm]
        if familyDes:
            return familyDes[0]
    if not familyDes:
        return parm+' Instance'

