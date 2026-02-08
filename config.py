import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    """
    Common configurations
    """

    # Put any configurations here that are common across all environments
    TESTING = False
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 6660))
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///base.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key')

    # openapi.info.description
    DESCRIPTION = '''
Easyun api docs:
* Swagger docs path: /api/docs
    '''
    SWAGGER_UI_CSS = 'https://fastly.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css'
    SWAGGER_UI_BUNDLE_JS = 'https://fastly.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js'
    SWAGGER_UI_STANDALONE_PRESET_JS = 'https://fastly.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js'

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
    'dev': DevelopmentConfig,
    'test': TestConfig,
    'prod': ProductionConfig,
}
