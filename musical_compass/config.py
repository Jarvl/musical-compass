import os

DEBUG = os.environ.get('DEBUG') == '1'

# Session
SESSION_TYPE = 'filesystem'
SECRET_KEY = os.getenv('SECRET_KEY')

# Database
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO') == '1'
