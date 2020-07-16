import os
import matplotlib.pyplot as plt
from flask import Flask, session, request, redirect, send_file
from flask_session import Session
from flask_talisman import Talisman
import pyoauth2
from . import helpers

app = Flask(__name__)
app.config.from_object("musical_compass.config")

Session(app)

# Talisman will only be enabled when flask is in debug mode
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

@app.route('/')
def index():
  if request.args.get("code"):
    session['authorized_client'] = spotify_client.auth_code.get_token(
      request.args.get("code"),
      redirect_uri=os.environ['SPOTIFY_REDIRECT_URI']
    )
    return redirect('/results')

  if not session.get('authorized_client'):
    auth_url = spotify_client.auth_code.authorize_url(redirect_uri=os.environ['SPOTIFY_REDIRECT_URI'], scope=scope)
    return f'<h2><a href="{auth_url}">Get Musical Compass Results</a></h2>'

  profile = session['authorized_client'].get('me/').parsed

  return '<h2>Hi, {} ' \
    '<div><a href="/results">Get Musical Compass Results</a></div>'.format(profile['display_name'])


@app.route('/.well-known/acme-challenge/kuGl8u6dAhjmmsY8ltItD4w1LsFtBPlIyQB-K5fb7XA')
def well_known():
  return 'kuGl8u6dAhjmmsY8ltItD4w1LsFtBPlIyQB-K5fb7XA.chY9M7gBNKq7G06W1sGE2RB7XK_reLfEs2vpTdYktQU'


@app.route('/sign_out')
def sign_out():
  session.clear()
  return redirect('/')


@app.route('/results')
def results():
  if not session.get('authorized_client'):
    return redirect('/')
  else:
    x_axis_key = 'acousticness'
    y_axis_key = 'valence'
    try:
      (x_axis_value, y_axis_value) = helpers.get_compass_values(x_axis_key, y_axis_key)
    except helpers.NoListeningDataException as e:
      return str(e)

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

    filename = 'generated_compasses/musical_compass-{}.png'.format(profile['id'])
    plt.savefig('musical_compass/{}'.format(filename))

    return send_file(filename, mimetype='image/png')
