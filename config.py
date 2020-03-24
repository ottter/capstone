import os

class Config(object):
    DEBUG = True
    TESTING = False

    SECRET_KEY = '2h80dh28ddh2hdi2Djdd2jhdjdDfhsff'
    SQLALCHEMY_DATABASE_URI =  'sqlite:///site.db'

    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True