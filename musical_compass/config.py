import os
import datetime
import redis

DEBUG = os.environ.get('DEBUG') == '1'

# Session
SECRET_KEY = os.getenv('SECRET_KEY')
SESSION_TYPE = 'redis'
SESSION_USE_SIGNER = True
SESSION_REDIS = redis.from_url(os.environ['REDIS_URL'])
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

# Database
# Heroku uses postgres:// for its URI but SQLAlchemy only accepts postgresql://
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
  SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO') == '1'

# Spotify
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URI = os.environ['SPOTIFY_REDIRECT_URI']
