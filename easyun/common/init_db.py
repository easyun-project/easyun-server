# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from easyun import db
from .models import Account, User, Datacenter


def init_database():
    db.create_all()

    # 预设Users
    demoUser = User(username='admin', email='admin@mail.com')
    demoUser.set_password('admin')
    db.session.add(demoUser)

    # 预设account
    demoAccount = Account(**{
        'cloud': 'aws', 
        'account_id':'666621994060',
        'role' : 'easyun-service-control-role',
        'region' : 'us-east-1',
        'aws_type': 'Global',
        "active_date": datetime.now(),
        "remind": True
    })
    db.session.add(demoAccount)

    # 预设datacenter
    demoDC = Datacenter(**{
        "name": "Easyun",
        "cloud": "aws",
        "account_id": "666621994060",
        "region": "us-east-1",
        "vpc_id": "vpc-057f0e3d715c24147",
        'hash': '6e40a16dd5f7e71200c9a72eb96419d3'
    })
    demoDC.set_hash('Easyun')
    db.session.add(demoDC)

    db.session.commit()
