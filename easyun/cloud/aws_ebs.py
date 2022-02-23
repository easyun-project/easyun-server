# -*- coding: utf-8 -*-
"""
  @module:  AWS EBS
  @desc:    Define basic attributes of AWS EBS.  
  @auth:    aleck
"""

Volume_Types = {
    "gp2": {
        "typeDes":"General Purpose SSD (gp2)",
        "volumeSize":[1,16384],
        "volumeIops": None,     #固定为volumeSize*100,
        "volumeThruput": None,
        "isMultiattach": False,
        "isBootvolume": True
    },
    "gp3": {
        "typeDes":"General Purpose SSD (gp3)",
        "volumeSize":[1,16384],
        "volumeIops":[3000, 16000],
        "volumeThruput":[1, 1000],
        "isMultiattach": False,
        "isBootvolume": True
    },
    "io1": {
        "typeDes":"Provisioned IOPS SSD (io1)",
        "volumeSize":[4,16384],
        "volumeIops":[100, 64000],
        "volumeThruput": None,
        "isMultiattach": True,
        "isBootvolume": True
    },
    "io2": {
        "typeDes":"Provisioned IOPS SSD (io2)",
        "volumeSize":[8,16384],
        "volumeIops":[100, 256000],
        "volumeThruput": None,
        "isMultiattach": True,
        "isBootvolume": True
    },
    "st1":{
        "typeDesc":"Throughput Optimized HDD (st1)",
        "volumeSize":[125,16384],
        "volumeIops": None,
        "volumeThruput": None,
        "isMultiattach": False,
        "isBootvolume": False
    },
    "sc1":{
        "typeDesc":"Cold HDD (sc1)",
        "volumeSize":[125,16384],
        "volumeIops": None,
        "volumeThruput": None,
        "isMultiattach": False,
        "isBootvolume": False
    },
    "standard":{
        "typeDesc":"Magnetic (standard)",
        "volumeSize":[1,1024],
        "volumeIops": None,
        "volumeThruput": None,
        "isMultiattach": False,
        "isBootvolume": True
    }    
}
