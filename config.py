import os

class Config(object):
    EMOJI = os.environ.get("EMOJI", True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class DebugConfig(Config):
    BASE_URL = "http://localhost:3000"
    DEBUG = True

class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI  = os.environ.get("DATABASE_URL") # Set by Heroku
