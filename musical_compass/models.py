from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

db = SQLAlchemy() # session_options={'autocommit': True}

class BaseMixin(object):
  created_at = db.Column(db.DateTime(), nullable=False, server_default=func.now())
  updated_at = db.Column(
    db.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()
  )
  # Makes sure the columns are added to the end of the table
  created_at._creation_order = 9998
  updated_at._creation_order = 9999

class UserAccount(BaseMixin, db.Model):
  id = db.Column(db.String, primary_key=True) # Spotify user ID
  results = db.relationship("Result", backref="user_account")

class Result(BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_account_id = db.Column(db.String, db.ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
  tracks = db.relationship("Track", secondary="result__track", backref="results", lazy="joined")

class Track(BaseMixin, db.Model):
  id = db.Column(db.String, primary_key=True) # Spotify track ID
  analytics_data = db.Column(postgresql.JSON(), nullable=False)

class Result_Track(BaseMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  result_id = db.Column(db.Integer, db.ForeignKey("result.id", ondelete="CASCADE"), nullable=False)
  track_id = db.Column(db.String, db.ForeignKey("track.id"), nullable=False)
  track_order = db.Column(db.Integer, nullable=False)
