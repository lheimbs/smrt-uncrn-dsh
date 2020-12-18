"""Flask config."""
import os

from dotenv import load_dotenv

from smrtuncrndsh import get_base_dir

BASE_DIR = get_base_dir()
load_dotenv(verbose=True)


class Config:
    """Flask configuration variables."""

    # General Config
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY')

    DISABLE_CACHE = os.environ.get("FLASK_APP_DISABLE_CACHE", "")
    DISABLE_FORCE_HTTPS = os.environ.get("FLASK_APP_DISABLE_FORCE_HTTPS", "")

    # Static Assets
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, os.environ.get("FLASK_APP_UPLOAD_FOLDER", "upload"))
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB

    OWM_API_KEY = os.environ.get("OWM_API_KEY", "")

    DEBUG = False
    TESTING = False
    DB_NAME = 'data'
    MQTT_SERVER = 'lennyspi.local'
    SECRET_KEY = 'key'
    ADMIN = {
        'username': os.environ.get('FLASK_APP_ADMIN', 'admin'),
        'email': os.environ.get('FLASK_APP_ADMIN_EMAIL', 'admin@admin.de'),
        'password': os.environ.get('FLASK_APP_ADMIN_PASSWORD', 'admin')
    }

    DROP_ALL = os.environ.get('FLASK_APP_DROP_ALL', '')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'

    SQLALCHEMY_BINDS = {
        'probe_request': 'sqlite:///data_probes.db',
        'users': 'sqlite:///data_users.db',
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SHOPPING_LISTS_PER_PAGE = 10

    CSP = {
        # Fonts from fonts.google.com
        'font-src': "'self' themes.googleusercontent.com *.gstatic.com",
        # Used by generated code from http://www.google.com/fonts
        'style-src': [
            "'self'",
            "ajax.googleapis.com fonts.googleapis.com ",
            "*.gstatic.com",
            "'unsafe-inline'",  # sucks but idk how to mitigate this sadly
        ],
        "script-src": [
            "'self'",
            # Due to https://github.com/plotly/dash/issues/630:
            "'sha256-jZlsGVOhUAIcH+4PVs7QuGZkthRMgvT2n0ilH6/zTM0='",
            # "'unsafe-inline'",
        ]
    }

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        os.environ.get('FLASK_APP_DATABASE_USER'),
        os.environ.get('FLASK_APP_DATABASE_PASSWORD'),
        os.environ.get('FLASK_APP_DATABASE_HOST'),
        os.environ.get('FLASK_APP_DATABASE_PORT'),
        os.environ.get('FLASK_APP_DATABASE_DATA_NAME')
    )

    SQLALCHEMY_BINDS = {
        'probe_request': 'postgresql://{}:{}@{}:{}/{}'.format(
            os.environ.get('FLASK_APP_DATABASE_USER'),
            os.environ.get('FLASK_APP_DATABASE_PASSWORD'),
            os.environ.get('FLASK_APP_DATABASE_HOST'),
            os.environ.get('FLASK_APP_DATABASE_PORT'),
            os.environ.get('FLASK_APP_DATABASE_PROBES_NAME')
        ),
        'users': 'postgresql://{}:{}@{}:{}/{}'.format(
            os.environ.get('FLASK_APP_DATABASE_USER'),
            os.environ.get('FLASK_APP_DATABASE_PASSWORD'),
            os.environ.get('FLASK_APP_DATABASE_HOST'),
            os.environ.get('FLASK_APP_DATABASE_PORT'),
            os.environ.get('FLASK_APP_DATABASE_USERS_NAME')
        ),
    }


class ProductionConfig(Config):
    """Uses production database server."""
    DEBUG = False

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


class DevelopmentConfig(Config):
    MQTT_SERVER = 'localhost'
    MQTT_PORT = 1883
    DEBUG = True


class OfflineConfig(Config):
    DEBUG = True
    MQTT_SERVER = 'localhost'
    MQTT_PORT = 1883
    DROP_ALL = True


class TestingConfig(Config):
    DB_NAME = 'data_testing'
    MQTT_SERVER = 'localhost'
    DEBUG = True


config_dict = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'offline': OfflineConfig,
}
