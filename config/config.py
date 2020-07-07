"""Flask config."""
import os
from dotenv import load_dotenv

from smrtuncrndsh import get_base_dir

BASE_DIR = get_base_dir()
print(f"config: {BASE_DIR}")
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """Flask configuration variables."""

    # General Config
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Static Assets
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    DEBUG = False
    TESTING = False
    MQTT_SERVER = 'lennyspi.local'
    SECRET_KEY = 'key'
    ADMIN = {
        'username': 'admin',
        'email': 'admin@admin.de',
        'password': 'admin'
    }

    DROP_ALL = os.environ.get('DROP_ALL', '')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'

    SQLALCHEMY_BINDS = {
        'probe_request': 'sqlite:///data_probes.db',
        'users': 'sqlite:///data_users.db',
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """Uses production database server."""
    DB_NAME = 'data_production'

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        os.environ.get('DATABASE_USER', 'lenny'),
        os.environ.get('DATABASE_PASSWORD', ''),
        os.environ.get('DATABASE_HOST', 'dashboard.heimbs.me'),
        os.environ.get('DATABASE_PORT', 65432),
        os.environ.get('DATABASE_NAME', 'data_production')
    )

    SQLALCHEMY_BINDS = {
        'probe_request': 'postgresql://{}:{}@{}:{}/{}'.format(
            os.environ.get('DATABASE_USER', 'lenny'),
            os.environ.get('DATABASE_PASSWORD', ''),
            os.environ.get('DATABASE_HOST', 'dashboard.heimbs.me'),
            os.environ.get('DATABASE_PORT', 65432),
            os.environ.get('DATABASE_NAME', 'probes_production')
        ),
        'users': 'postgresql://{}:{}@{}:{}/{}'.format(
            os.environ.get('DATABASE_USER', 'lenny'),
            os.environ.get('DATABASE_PASSWORD', ''),
            os.environ.get('DATABASE_HOST', 'dashboard.heimbs.me'),
            os.environ.get('DATABASE_PORT', 65432),
            os.environ.get('DATABASE_NAME', 'users_production')
        ),
    }


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        os.environ.get('DATABASE_USER', 'pi'),
        os.environ.get('DATABASE_PASSWORD', ''),
        os.environ.get('DATABASE_HOST', 'lennyspi.local'),
        os.environ.get('DATABASE_PORT', 5432),
        os.environ.get('DATABASE_NAME', 'data')
    )

    SQLALCHEMY_BINDS = {
        'probe_request': 'postgresql://{}:{}@{}:{}/{}'.format(
            os.environ.get('DATABASE_USER', 'pi'),
            os.environ.get('DATABASE_PASSWORD', ''),
            os.environ.get('DATABASE_HOST', 'lennyspi.local'),
            os.environ.get('DATABASE_PORT', 5432),
            os.environ.get('DATABASE_NAME', 'probes')
        ),
        'users': 'postgresql://{}:{}@{}:{}/{}'.format(
            os.environ.get('DATABASE_USER', 'pi'),
            os.environ.get('DATABASE_PASSWORD', ''),
            os.environ.get('DATABASE_HOST', 'lennyspi.local'),
            os.environ.get('DATABASE_PORT', 5432),
            os.environ.get('DATABASE_NAME', 'users')
        ),
    }
    MQTT_SERVER = 'localhost'
    MQTT_PORT = 1883
    DEBUG = True


class OfflineConfig(Config):
    DEBUG = True
    MQTT_SERVER = 'localhost'
    MQTT_PORT = 1883
    DROP_ALL = True


class TestingConfig(Config):
    MQTT_SERVER = 'localhost'
    DEBUG = True


config_dict = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'offline': OfflineConfig,
}
