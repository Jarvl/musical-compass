import os

DEBUG = os.environ.get('DEBUG') == '1'

# Session
SESSION_TYPE = 'filesystem'
SECRET_KEY = os.getenv('SECRET_KEY')