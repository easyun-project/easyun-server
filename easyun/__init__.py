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


# define api version
ver = '/api/v1.0'

# extensions initialization
db = SQLAlchemy()
cors = CORS()

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

    migrate = Migrate(app, db, compare_type=True)

    register_blueprints(app)
    configure_logger(app)

    app.logger.setLevel(logging.INFO)
    if run_env != 'test':
        app.logger.info('Easyun API Start')

    return app


# 注册 Flask blueprints
def register_blueprints(app):
    """Register Flask blueprints."""
    from .common import auth
    from .modules import mserver
    from .modules import datacenter

    app.register_blueprint(auth.bp)
    app.register_blueprint(mserver.bp)
    app.register_blueprint(datacenter.bp)
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

def register_extensions(app:APIFlask):
    """初始化扩展

    Args:
        app (APIFlask): application实例
    """
    db.init_app(app)
    cors.init_app(app)

def register_commands(app:APIFlask):
    """注册自定义命令

    Args:
        app (APIFlask): application实例
    """
    @app.cli.command()
    def initdb():
        db.create_all()
        click.echo("init dev databses.")
    
    @app.cli.command()
    def dropdb():
        db.drop_all()
        click.echo("drop dev databses.")
