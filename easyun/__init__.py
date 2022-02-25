# -*- coding: UTF-8 -*-
'''
@Description: The app module, containing the app factory function.
@LastEditors: 
'''

import os
import logging
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer, Field, Nested
from logging.handlers import RotatingFileHandler
import click
from flask_sqlalchemy import SQLAlchemy
from config import env_config
from flask_cors import CORS
from flask_migrate import Migrate
# from .common.result import BaseResponseSchema
from config import Config
from easyun.libs.celery import FlaskCelery
from easyun.libs.log import EasyunLogging

# define api version
ver = '/api/v1'

#保留 FLAG 用于兼容旧代码
FLAG = "Easyun"

# extensions initialization
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
celery = FlaskCelery(
        __name__,
        broker=Config.CELERY_broker_url,
        backend=Config.result_backend
    )
log = EasyunLogging()


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

    app.logger.setLevel(logging.INFO)
    if run_env != 'test':
        app.logger.info('Easyun API Start')

    # 初始化AWS云环境账号基础信息
    register_aws_account(app)

    return app


# 注册 Flask blueprints
def register_blueprints(app: APIFlask):
    """Register Flask blueprints."""
    from .common import auth
    from .modules import mserver, mstorage, datacenter, account, dashboard, mdatabase

    app.register_blueprint(auth.bp)
    app.register_blueprint(datacenter.bp)
    app.register_blueprint(mserver.bp)
    app.register_blueprint(mdatabase.bp)
    app.register_blueprint(mstorage.bp)
    app.register_blueprint(account.bp)    
    app.register_blueprint(dashboard.bp)
    return None

def register_extensions(app: APIFlask):
    """初始化扩展

    Args:
        app (APIFlask): application实例
    """
    db.init_app(app)
    cors.init_app(app)
    celery.init_app(app)
    log.init_app(app)

    with app.app_context():
        # 初始化数据库
        from easyun.common.models import User, Account, Datacenter
        db.create_all()
        if db.engine.url.drivername == 'sqlite':
            # dev test
            migrate.init_app(app, db, render_as_batch=True, compare_type=True)
        else:
            migrate.init_app(app, db, compare_type=True)


def register_aws_account(app: APIFlask):
    """注册后端服务器部署的云账号信息"""
    from easyun.common.models import Account
    from easyun.cloud.aws_basic import get_deploy_env
    # 获取 AWS云环境信息
    awsEnv = get_deploy_env('aws')
    # 数据写入 database
    with app.app_context():
        exist_account:Account = Account.query.filter_by(cloud='aws').first()
        if exist_account:
            exist_account.update_dict(awsEnv)
        else:
            aws_account = Account(
                cloud='aws', 
                account_id = awsEnv.get('account_id'), 
                role = awsEnv.get('role'),  
                deploy_region = awsEnv.get('deploy_region'), 
                aws_type = awsEnv.get('aws_type'), 
                )
            db.session.add(aws_account)
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
        #     "aww_type": "Global",
        #     "active_date": datetime.now(),
        #     "remind": True
        # })
        # db.session.add(account)
        db.session.commit()
        click.echo("init dev database.")

    @app.cli.command()
    def dropdb():
        db.drop_all()
        click.echo("drop dev database.")
