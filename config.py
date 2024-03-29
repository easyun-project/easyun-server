import os


class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments
    TESTING = False
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///base.db'
    # 设置sqlalchemy自动跟踪数据库修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # openapi.info.description
    DESCRIPTION = '''
Easyun api docs:
* Swagger docs path: /api/docs
* redoc path: /api/redoc'
    '''
    SWAGGER_UI_CSS = 'https://fastly.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'
    SWAGGER_UI_BUNDLE_JS = 'https://fastly.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js'
    SWAGGER_UI_STANDALONE_PRESET_JS = 'https://fastly.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js'
    REDOC_STANDALONE_JS = 'https://fastly.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'

    # celery for async
    # CELERY_broker_url = 'redis://localhost:6379/0'
    # result_backend = 'redis://localhost:6379/1'

    # Using SQLAlchemy Broker for local development
    CELERY_broker_url = 'sqla+sqlite:///celery/borker.db'
    result_backend = 'db+sqlite:///celery/results.db'

    # openapi.servers
    SERVERS = [
        {'name': 'Development Server', 'url': 'http://127.0.0.1:6660'},
        {'name': 'Testing Server', 'url': 'http://35.76.66.98:6660'},
    ]

    # openapi.externalDocs
    EXTERNAL_DOCS = {
        'description': 'Find more info here',
        'url': 'https://boto3.amazonaws.com/v1/documentation/api/latest/guide/index.html',
    }


class TestConfig(Config):
    """
    Testing configurations
    """

    TESTING = True
    FLASK_DEBUG = True
    SQLALCHEMY_ECHO = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    FLASK_DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    FLASK_DEBUG = False
    SQLALCHEMY_ECHO = False


env_config = {
    'test': TestConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
