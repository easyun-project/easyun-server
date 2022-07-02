# -*- coding: UTF-8 -*-
'''
@Description: The app module, containing the app factory function.
@LastEditors:
'''

import os
import logging
from apiflask import APIFlask, Schema
from apiflask.fields import String, Integer, Field
# from logging.handlers import RotatingFileHandler
import click
from flask_sqlalchemy import SQLAlchemy
# from flask_redis import FlaskRedis
from config import env_config
from flask_cors import CORS
from flask_migrate import Migrate
# from .common.result import BaseResponseSchema
from config import Config
from easyun.libs.celery import FlaskCelery
from easyun.libs.log import EasyunLogging


# define api version
ver = '/api/v1'

# 保留 FLAG 用于兼容旧代码
FLAG = "Easyun"

# extensions initialization
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
celery = FlaskCelery(
    __name__, broker=Config.CELERY_broker_url, backend=Config.result_backend
)
log = EasyunLogging()
# redis_client = FlaskRedis()


class BaseResponseSchema(Schema):
    message = String()
    detail = Field()  # the data key
    status_code = Integer()  # the HTTP_STATUS_CODES
    task = Field()  # the task status


def create_app(run_env=None):
    if run_env is None:
        run_env = os.getenv("FLASK_CONFIG", 'development')

    app = APIFlask(__name__, docs_path='/api/docs', redoc_path='/api/redoc')
    app.config.from_object(env_config[run_env])
    # schema for generic response
    app.config['BASE_RESPONSE_SCHEMA'] = BaseResponseSchema
    # the data key should match the data field name in the base response schema
    # defaults to "data"
    app.config['BASE_RESPONSE_DATA_KEY'] = 'detail'

    # 初始化扩展
    register_extensions(app=app)
    # 注册自定义命令
    register_commands(app=app)
    # 全局日志
    app.logger.setLevel(logging.INFO)
    if run_env != 'test':
        app.logger.info(f'Easyun API Start [{run_env}]')

    # 初始化AWS云环境账号基础信息
    register_cloud_account(app)

    # @app.error_processor
    # def validation_error_proc(error):
    #     err_resp = {
    #         'detail': error.detail.get('json'),
    #         'message': error.message,
    #     }
    #     return err_resp, error.status_code, error.headers

    @app.route('/', methods=['GET'])
    def default_page():
        resp = {
            'detail': {'status': 'running'},
            'message': 'success'
        }
        return resp

    # 注册子模块blueprint
    register_blueprints(app)

    return app


def register_extensions(app: APIFlask):
    """初始化扩展

    Args:
        app (APIFlask): application实例
    """
    db.init_app(app)
    cors.init_app(app)
    celery.init_app(app)
    log.init_app(app)
    # redis_client.init_app(app)

    with app.app_context():
        # 初始化数据库
        from easyun.common.models import User, Account, Datacenter

        db.create_all()
        if db.engine.url.drivername == 'sqlite':
            # dev test
            migrate.init_app(app, db, render_as_batch=True, compare_type=True)
        else:
            migrate.init_app(app, db, compare_type=True)


def register_cloud_account(app: APIFlask):
    """注册后端服务器部署的云账号信息"""
    from easyun.common.models import Account
    from easyun.cloud import get_deploy_env

    # 获取 AWS云环境信息
    cloudEvn = get_deploy_env()
    # 数据写入 database
    with app.app_context():
        existAccount: Account = Account.query.filter_by(cloud='aws').first()
        if existAccount:
            existAccount.update_dict(cloudEvn)
        else:
            thisAccount = Account(
                cloud='aws',
                account_id=cloudEvn.get('accountId'),
                role=cloudEvn.get('role'),
                deploy_region=cloudEvn.get('deployRegion'),
                aws_type=cloudEvn.get('regionType'),
            )
            db.session.add(thisAccount)
        db.session.commit()


# 注册 Flask blueprints
def register_blueprints(app: APIFlask):
    """Register Flask blueprints."""
    from .common import auth
    from .modules import mserver, mstorage, datacenter, account, dashboard, mdatabase, mloadbalancer

    app.register_blueprint(auth.bp)
    app.register_blueprint(datacenter.bp)
    app.register_blueprint(mserver.bp)
    app.register_blueprint(mstorage.bp)
    app.register_blueprint(mdatabase.bp)    
    app.register_blueprint(mloadbalancer.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(account.bp)
    return None


def register_commands(app: APIFlask):
    """注册自定义命令
    Args:
        app (APIFlask): application实例
    """

    @app.cli.command()
    def initdb():
        from easyun.common.models import User, Account, Datacenter, KeyStore, KeyPairs

        db.create_all()
        # 预设 demo user
        demoUser = User(username='demo', email='demo@easyun.com')
        demoUser.set_password('easyun')
        db.session.add(demoUser)

        db.session.commit()
        click.echo("init dev database.")

    @app.cli.command()
    def dropdb():
        db.drop_all()
        click.echo("drop dev database.")
