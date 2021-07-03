import os
import json
import matplotlib.pyplot as plt
from flask import Flask, session, request, redirect, send_file
from flask_migrate import Migrate
from flask_session import Session
from flask_talisman import Talisman
import sqlalchemy
from sqlalchemy.dialects import postgresql
import pyoauth2

from . import helpers, models

app = Flask(__name__)
app.config.from_object("musical_compass.config")
Session(app)
migrate = Migrate(app, models.db)
models.db.init_app(app)
Talisman(
  app,
  force_https=True,
  force_https_permanent=True,
  content_security_policy=None,
)

api_url = 'https://api.spotify.com/v1/'
scope = 'user-top-read'
spotify_client = pyoauth2.Client(
  os.environ['SPOTIFY_CLIENT_ID'],
  os.environ['SPOTIFY_CLIENT_SECRET'],
  site=api_url,
  authorize_url='https://accounts.spotify.com/authorize',
  token_url='https://accounts.spotify.com/api/token'
)
auth_url = spotify_client.auth_code.authorize_url(redirect_uri=os.environ['SPOTIFY_REDIRECT_URI'], scope=scope)

@app.route('/')
def index():
  # TODO: replace with view
  content = '<div><a href="{}">Get Musical Compass Results</a></div>'.format(auth_url)
  if session.get('authorized_client'):
    profile = session['authorized_client'].get('me/').parsed
    content = '<h2>Hi, {}</h2>'.format(profile['display_name']) + content
  return content


@app.route('/callback')
def callback():
  if request.args.get("code"):
    session['authorized_client'] = spotify_client.auth_code.get_token(
      request.args.get("code"),
      redirect_uri=os.environ['SPOTIFY_REDIRECT_URI']
    )
    return redirect('/results')
  else:
    return redirect('/')


@app.route('/sign_out')
def sign_out():
  session.clear()
  return redirect('/')


@app.route('/results')
def results():
  if not session.get('authorized_client'):
    return redirect('/')
  else:
    try:
      top_track_ids = helpers.get_top_track_ids()
    except helpers.NoListeningDataException as e:
      return str(e)

    top_track_audio_features = helpers.get_audio_features(top_track_ids)
    top_track_ids_with_analytics = [x['id'] for x in top_track_audio_features]

    x_axis_key = 'acousticness'
    y_axis_key = 'valence'
    (x_axis_value, y_axis_value) = helpers.get_compass_values(
      top_track_audio_features,
      x_axis_key,
      y_axis_key
    )

    # Plot it
    fig, ax = plt.subplots(figsize=(15, 12))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    ax.axvline(0, color = 'black', linestyle='dashed', lw=2)
    ax.axhline(0, color = 'black', linestyle='dashed', lw=2)

    x_axis_title = x_axis_key.title()
    y_axis_title = 'Happiness'

    plot_title = 'Musical Compass\n{}: {}, {}: {}'.format(
      x_axis_title,
      round(x_axis_value, 2),
      y_axis_title,
      round(y_axis_value, 2)
    )

    ax.set_title(plot_title)
    ax.set_xlabel(x_axis_title)
    ax.set_ylabel(y_axis_title)

    ax.fill_between([-1, 0],0,-1,alpha=1, color='#c8e4bc')  # LibLeft
    ax.fill_between([0, 1], -1, 0, alpha=1, color='#f5f5a7')  # LibRight
    ax.fill_between([-1, 0], 0, 1, alpha=1, color='#f9baba')  # AuthLeft
    ax.fill_between([0, 1], 0, 1, alpha=1, color='#92d9f8')  # AuthRight
    ax.fill_between([-.3, .3], -.3, .3, alpha=1, color='#808080')  # Grill

    plt.plot(x_axis_value, y_axis_value, 'ro')

    # plt.show()

    profile = session['authorized_client'].get('me/').parsed

    # Upsert user account record
    user_account = models.UserAccount.query.filter_by(id=profile['id']).first()
    if not user_account:
      user_account = models.UserAccount(id=profile['id'])
      models.db.session.add(user_account)
      models.db.session.commit()
      models.db.session.refresh(user_account)

    # Only save current result in db if the current result tracks (in order)
    # are different from the last time the user got a result

    create_new_result = True

    last_result = models.Result.query.order_by(models.Result.created_at.desc()).first()
    if last_result:
      last_result_track_ids_ordered = [
        x.track_id for x in
        models.Result_Track.query
        .filter_by(result_id=last_result.id)
        .order_by(models.Result_Track.track_order.asc())
      ]
      if last_result_track_ids_ordered and last_result_track_ids_ordered == top_track_ids_with_analytics:
          create_new_result = False

    if create_new_result:
      # Create result record
      result = models.Result(user_account_id=user_account.id)
      models.db.session.add(result)
      models.db.session.commit()
      models.db.session.refresh(result)

      # Create track records
      analytics_data_keys = [
        'danceability',
        'energy',
        'key',
        'loudness',
        'mode',
        'speechiness',
        'acousticness',
        'instrumentalness',
        'liveness',
        'valence',
        'tempo',
        'duration_ms',
        'time_signature',
      ]
      track_upsert_statement = (
        postgresql.insert(models.Track)
        .values([
          {
            "id": x['id'],
            "analytics_data": json.dumps({ k: v for (k, v) in x.items() if k in analytics_data_keys })
          }
          for x in top_track_audio_features
        ])
        .on_conflict_do_nothing()
      )
      track_upsert_result = models.db.engine.execute(track_upsert_statement)
      models.db.session.commit()

      # Create result_track join table records
      result_track_records = [
        models.Result_Track(result_id=result.id, track_id=track_id, track_order=track_order)
        for track_order, track_id in enumerate(top_track_ids_with_analytics, start=1)
      ]
      models.db.session.bulk_save_objects(result_track_records)
      models.db.session.commit()

    filename = 'generated_compasses/musical_compass-{}.png'.format(profile['id'])
    plt.savefig('musical_compass/{}'.format(filename))

    return send_file(filename, mimetype='image/png')
