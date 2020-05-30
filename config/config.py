import os

from dotenv import load_dotenv
load_dotenv(verbose=True)


class Config(object):
    """Base config, uses staging database server."""
    DEBUG = False
    TESTING = False
    DB_NAME = 'data'
    MQTT_SERVER = 'lennyspi.local'

    @property
    def SQLALCHEMY_DATABASE_URI(self):         # Note: all caps
        return f'postgresql://pi:{os.getenv("DATABASE_PASSWORD")}@lennyspi.local/{self.DB_NAME}'

    @property
    def SQLALCHEMY_BINDS(self):
        return {
            'probe_request': f'postgresql://pi:{os.getenv("DATABASE_PASSWORD")}@lennyspi.local/{self.DB_NAME}_probes'
        }


class ProductionConfig(Config):
    """Uses production database server."""
    DB_NAME = 'data_production'
    MQTT_SERVER = 'lennyspi.local'


class DevelopmentConfig(Config):
    DB_NAME = 'data_development'
    MQTT_SERVER = 'localhost'
    MQTT_PORT = 1883
    DEBUG = True


class TestingConfig(Config):
    DB_NAME = 'data_testing'
    MQTT_SERVER = 'localhost'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
