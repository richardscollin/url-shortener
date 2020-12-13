import os

class Config(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class HerokuConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI  = os.environ.get("DATABASE_URL") # Set by Heroku
