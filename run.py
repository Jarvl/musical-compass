import matplotlib.pyplot as plt
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

username = os.environ.get('USERNAME')
scope = 'user-top-read'

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, username=username))

def convert_to_plot_range(value):
  return (((value - 0) * (1 - -1)) / (1 - 0)) + -1

def get_weight(track_number):
  # First track will start at 0
  x = (track_number - 1) / 10
  y = 1 / 2 ** (x / 0.75)
  return y

def get_top_tracks():
  # Last 6 months
  return spotify.current_user_top_tracks(limit=50, offset=0, time_range='medium_term')['items']

top_track_ids = [ x['id'] for x in get_top_tracks()]
top_track_audio_features = spotify.audio_features(tracks=top_track_ids)

total_tracks = len(top_track_audio_features)
track_number = 0
total_acousticness = 0
total_valence = 0
weight_sum = 0

for track_features in top_track_audio_features:
  weight = get_weight(track_number)
  total_acousticness += (track_features['acousticness'] * weight)
  total_valence += (track_features['valence'] * weight)
  weight_sum += weight
  track_number += 1

# Weighted average (divide by the sum of all weights)
mean_acousticness = convert_to_plot_range(total_acousticness / weight_sum)
mean_valence = convert_to_plot_range(total_valence / weight_sum)

print('mean_acousticness: {}'.format(mean_acousticness))
print('mean_valence: {}'.format(mean_valence))

# mean_acousticness = convert_to_plot_range(0.27118336234572343)
# mean_valence = convert_to_plot_range(0.554849439269494)

fig,ax = plt.subplots(figsize=(15, 12))
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)

ax.axvline(0, color = 'black', linestyle='dashed', lw=2)
ax.axhline(0, color = 'black', linestyle='dashed', lw=2)

ax.set_title('Musical Compass')
ax.set_ylabel('Happiness')
ax.set_xlabel('Acousticness')

ax.fill_between([-1, 0], 0, -1, alpha=1, color='#c8e4bc')  # LibLeft
ax.fill_between([0, 1], -1, 0, alpha=1, color='#f5f5a7')  # LibRight
ax.fill_between([-1, 0], 0, 1, alpha=1, color='#f9baba')  # AuthLeft
ax.fill_between([0, 1], 0, 1, alpha=1, color='#92d9f8')  # AuthRight

plt.plot(mean_acousticness, mean_valence, 'ro')

plt.show()