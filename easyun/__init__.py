# -*- coding: UTF-8 -*-
'''
@Description: The app module, containing the app factory function.
@LastEditors: 
'''
from datetime import datetime
import os
import logging
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer, Field, Nested
from logging.handlers import RotatingFileHandler
import click
import boto3
from flask_sqlalchemy import SQLAlchemy
from config import env_config
from flask_cors import CORS
from flask_migrate import Migrate
# from .common.result import BaseResponseSchema


# define api version
ver = '/api/v1.0'

# extensions initialization
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()


class BaseResponseSchema(Schema):
    message = String()
    status_code = Integer()     # the HTTP_STATUS_CODES
    detail = Field()      # the data key


def create_app(run_env=None):
    if run_env is None:
        run_env = os.getenv("FLASK_CONFIG", 'development')

    app = APIFlask(__name__, docs_path='/api/docs', redoc_path='/api/redoc')
    app.config.from_object(env_config[run_env])

    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema
    # the data key should match the data field name in the base response schema
    # defaults to "data"
    app.config['BASE_RESPONSE_DATA_KEY'] = 'detail'

    # 初始化扩展
    register_extensions(app=app)

    # 注册自定义命令
    register_commands(app=app)

    register_blueprints(app)
    configure_logger(app)

    app.logger.setLevel(logging.INFO)
    if run_env != 'test':
        app.logger.info('Easyun API Start')

    # 初始化云环境基础信息
    set_cloud_env(app)

    return app


# 注册 Flask blueprints
def register_blueprints(app: APIFlask):
    """Register Flask blueprints."""
    from .common import auth
    from .modules import mserver
    from .modules import datacenter
    from .modules import account

    app.register_blueprint(auth.bp)
    app.register_blueprint(mserver.bp)
    app.register_blueprint(datacenter.bp)
    app.register_blueprint(account.bp)
    return None


def configure_logger(app):
    """Configure loggers."""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/easyun_api.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        if not app.logger.handlers:
            app.logger.addHandler(file_handler)


def register_extensions(app: APIFlask):
    """初始化扩展

    Args:
        app (APIFlask): application实例
    """
    db.init_app(app)
    cors.init_app(app)

    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            # dev test
            migrate.init_app(app, db, render_as_batch=True, compare_type=True)
        else:
            migrate.init_app(app, db, compare_type=True)


def set_cloud_env(app: APIFlask):
    """设置云环境基础信息"""
    from easyun.common.models import Account
    client_sts = boto3.client('sts')
    # 获取 account_id
    account_id = client_sts.get_caller_identity().get('Account')
    # 获取 iam_role
    role = client_sts.get_caller_identity().get('Arn').split('/')[1]
    # 获取 deployed region
    this_region = boto3.session.Session().region_name
    # 判断 account_type
    gcr_regions = ['cn-north-1', 'cn-northwest-1']
    if this_region in gcr_regions:
        aws_type = 'GCR'
    else:
        aws_type = 'Global'

    # 数据写入 database
    with app.app_context():
        exist_account = Account.query.filter_by(cloud='aws').first()
        if exist_account:
            exist_account.update_aws(account_id=account_id, role=role, deploy_region=this_region,aws_type=aws_type)
        else:
            this_account = Account(cloud='aws', account_id=account_id, role=role, deploy_region=this_region,aws_type=aws_type)
            db.session.add(this_account)
        db.session.commit()


def register_commands(app: APIFlask):
    """注册自定义命令

    Args:
        app (APIFlask): application实例
    """
    @app.cli.command()
    def initdb():
        from easyun.common.models import User, Account, Datacenter
        db.create_all()
        # 预设user
        admin = User(username='admin', email='admin@mail.com')
        admin.set_password('admin')
        db.session.add(admin)

        # 预设datacenter
        # center = Datacenter(**{
        #     "id": "1",
        #     "name": "Easyun",
        #     "cloud": "aws",
        #     "account_id": "666621994060",
        #     "region": "us-east-1",
        #     "vpc_id": "vpc-057f0e3d715c24147"
        # })
        # db.session.add(center)

        # 预设account
        # account = Account(**{
        #     "id": "1",
        #     "cloud": "aws",
        #     "account_id": "567820214060",
        #     "role": "easyun-service-control-role",
        #     "type": "Global",
        #     "active_date": datetime.now(),
        #     "remind": True
        # })
        # db.session.add(account)
        db.session.commit()
        click.echo("init dev databses.")

    @app.cli.command()
    def dropdb():
        db.drop_all()
        click.echo("drop dev databses.")
