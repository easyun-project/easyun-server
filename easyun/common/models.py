# -*- coding: UTF-8 -*-
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.sql.expression import true
from werkzeug.security import check_password_hash, generate_password_hash
from easyun import db
import sqlalchemy as sa

from easyun.common.exception.model_errs import KeyPairsRepeat

def universal_update_dict(obj, d: Dict):
    """批量更新数据库

    Args:
        obj (Model): 模型对象
        dict (dict): 内容字典
    """
    for key, value in d.items():
        if key in obj.__dict__:
            setattr(obj, key, value)


class User(db.Model):
    """
    Create a User table
    """
    __tablename__ = 'users'
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(60), unique=True)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def __init__(self, username=None, password=None, email=None, token=None, token_expiration=None):
        self.username = username
        if password is not None:
            self.password_hash = generate_password_hash(password)
        self.email = email
        self.token = token
        self.token_expiration = token_expiration

    def set_password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return (self.id)

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data and data[field]:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=7200):  # 设置 2 小时过期
        utcnow = datetime.utcnow()
        if self.token and self.token_expiration > utcnow + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = utcnow + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def update_dict(self, items: Dict):
        universal_update_dict(self, items)


class Account(db.Model):
    """
    Create a Account table
    """
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    cloud = db.Column(db.String(10), nullable=False)     # AWS
    account_id = db.Column(db.String(20), nullable=False,
                           unique=True)  # e.g. 567820214060
    # e.g easyun-service-control-role
    role = db.Column(db.String(100), nullable=False)
    # Easyun deploy region
    deploy_region = db.Column(db.String(60), nullable=False)
    aws_type = db.Column(db.String(10))        # Global / GCR
    active_date = db.Column(db.Date)           # Account Activation date
    remind = db.Column(db.Boolean)

    def update_aws(self, account_id, role, deploy_region, aws_type):
        self.account_id = account_id
        self.role = role
        self.deploy_region = deploy_region
        self.aws_type = aws_type

    def get_role(self):
        return (self.role)

    def get_region(self):
        return (self.deploy_region)

    def get_days(self):
        now = datetime.now()
        nowday = datetime.date(now)
        days = nowday - self.atvdate
        return days

    def update_dict(self, items: Dict):
        universal_update_dict(self, items)


class Datacenter(db.Model):
    """
    Create a Account table
    """
    __tablename__ = 'datacenter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False,
                     unique=True)    # Datacenter Name: Easyun
    # Cloud Provider: AWS
    cloud = db.Column(db.String(20), nullable=False)
    account_id = db.Column(
        db.String(30), nullable=False)           # Account ID
    region = db.Column(db.String(120))          # Deployed Region
    vpc_id = db.Column(db.String(120))           # VPC ID
    # Datacenter Create date
    create_date = db.Column(db.DateTime)

    def get_region(self):
        return (self.region)

    def update_dict(self, items: Dict):
        universal_update_dict(self, items)

class KeyPairs(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    region = sa.Column(sa.String(120))
    name = sa.Column(sa.String(20))
    material = sa.Column(sa.String(2048), nullable=False)
    extension = sa.Column(sa.String(10), default='pem')

    @staticmethod
    def New(**kwargs:dict):
        print(kwargs, type(kwargs))
        region_keys:List[KeyPairs] = KeyPairs.query.filter(
                                        KeyPairs.region == kwargs.get('region'),
                                        KeyPairs.name == kwargs.get('name')).count()
        # maybe use one_or_none function well be best?
        if region_keys > 0:
            raise KeyPairsRepeat('key pair name was in this region')

        return KeyPairs(**kwargs)

    def delet(region = None, name = None):
        pass

    def update(self, **kwargs):
        self.region = kwargs.get('region', self.region)
        self.name == kwargs.get('name', self.name)
        self.material = kwargs.get('material', self.material)
        self.extension = kwargs.get('extension', self.extension)
