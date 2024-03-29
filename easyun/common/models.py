# -*- coding: UTF-8 -*-
"""
  @module:  Easyun Common Models
  @desc:    Easyun通用modesl定义
  @auth:    
"""

import os
import base64
import hashlib
import sqlalchemy as sa
from datetime import datetime, date, timedelta
from typing import Dict, List
from werkzeug.security import check_password_hash, generate_password_hash
from easyun import db
from easyun.common.exception.model_errs import KeyPairsRepeat


def universal_update_dict(obj, dict: Dict):
    """批量更新数据库
    Args:
        obj (Model): 模型对象
        dict (dict): 内容字典
    """
    for key, value in dict.items():
        if key in obj.__dict__:
            setattr(obj, key, value)


class User(db.Model):
    """
    Create User table
    """

    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), nullable=False, unique=True)
    passwordHash = db.Column('password_hash', db.String(128), nullable=False)
    email = db.Column('email', db.String(60), unique=True)
    token = db.Column('token', db.String(32), index=True, unique=True)
    tokenExpiration = db.Column('token_expiration', db.DateTime)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def __init__(
        self,
        username=None,
        password=None,
        email=None,
        token=None,
        token_expiration=None,
    ):
        self.username = username
        if password is not None:
            self.passwordHash = generate_password_hash(password)
        self.email = email
        self.token = token
        self.tokenExpiration = token_expiration

    def set_password(self, password):
        """
        Set password to a hashed password
        """
        self.passwordHash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.passwordHash, password)

    def get_id(self):
        return self.id

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data and data[field]:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=7200):  # 设置 2 小时过期
        utcnow = datetime.utcnow()
        if self.token and self.tokenExpiration > utcnow + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.tokenExpiration = utcnow + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.tokenExpiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.tokenExpiration < datetime.utcnow():
            return None
        return user

    def update_dict(self, items: Dict):
        universal_update_dict(self, items)


class Account(db.Model):
    """
    Create Cloud Account table
    """

    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    cloud = db.Column(db.String(10), nullable=False)  # AWS
    account_id = db.Column(
        db.String(20), nullable=False, unique=True
    )  # e.g. 567820211120
    # e.g easyun-service-control-role
    role = db.Column(db.String(100), nullable=False)
    # Easyun deploy region
    deploy_region = db.Column(db.String(60), nullable=False)
    aws_type = db.Column(db.String(10))  # Global / GCR
    active_date = db.Column(db.Date)  # Account Activation date
    remind = db.Column(db.Boolean)

    def update_dict(self, items: Dict):
        universal_update_dict(self, items)

    def update_account(self, account_id, role, deploy_region, aws_type):
        self.account_id = account_id
        self.role = role
        self.deploy_region = deploy_region
        self.aws_type = aws_type
    
    def disable_remind(self):
        self.remind = False

    def get_role(self):
        return self.role

    def get_region(self):
        return self.deploy_region

    def get_days(self):
        nowDate = date.today()
        dateDelta = nowDate - self.active_date
        return dateDelta.days


class Datacenter(db.Model):
    """
    Create DataCenter table
    """

    __tablename__ = 'datacenter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)  # Datacenter name
    cloud = db.Column(db.String(20), nullable=False)  # Cloud Provider: AWS
    account_id = db.Column(db.String(30), nullable=False)  # Account ID
    region = db.Column(db.String(120))  # Deployed Region
    vpc_id = db.Column(db.String(120))  # VPC ID
    hash = db.Column(db.String(32), nullable=True)  # Hash code for tag:Flag
    create_date = db.Column(db.DateTime)  # Create date
    create_user = db.Column(db.String(30), nullable=True)  # Cteated by easyun user

    def set_hash(self, name):
        """
        Generate a hash code
        """
        self.hash = hashlib.md5(name.encode(encoding='UTF-8')).hexdigest()

    def get_region(self):
        return self.region

    def get_vpc(self):
        return self.vpc_id

    def get_hash(self):
        if self.hash is None:
            self.hash = hashlib.md5(self.name.encode(encoding='UTF-8')).hexdigest()
        return self.hash

    def update_dict(self, items: Dict):
        universal_update_dict(self, items)


class KeyStore(db.Model):
    """
    Create Keypair store table
    """

    __tablename__ = 'key_store'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    dc_name = db.Column(db.String(255), nullable=False)
    material = db.Column(db.String(2048))
    format = db.Column(db.String(10), default='pem')

    def get_material(self):
        if self.material:
            return self.material
        else:
            return None


class KeyPairs(db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    region = sa.Column(sa.String(120))
    name = sa.Column(sa.String(20))
    material = sa.Column(sa.String(2048), nullable=False)
    extension = sa.Column(sa.String(10), default='pem')

    @staticmethod
    def New(**kwargs: dict):
        print(kwargs, type(kwargs))
        region_keys: List[KeyPairs] = KeyPairs.query.filter(
            KeyPairs.region == kwargs.get('region'), KeyPairs.name == kwargs.get('name')
        ).count()
        # maybe use one_or_none function well be best?
        if region_keys > 0:
            raise KeyPairsRepeat('key pair name was in this region')

        return KeyPairs(**kwargs)

    def delete(region=None, name=None):
        pass

    def update(self, **kwargs):
        self.region = kwargs.get('region', self.region)
        self.name == kwargs.get('name', self.name)
        self.material = kwargs.get('material', self.material)
        self.extension = kwargs.get('extension', self.extension)
