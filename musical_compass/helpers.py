from functools import reduce
from flask import session

class NoListeningDataException(Exception):
  def __init__(self, message='You have no listening data to analyze yet!'):
    self.message = message
    super().__init__(self.message)

def convert_to_plot_range(value):
  return (((value - 0) * (1 - -1)) / (1 - 0)) + -1

def get_weight(track_number):
  weight = 1.0
  for _ in range(track_number):
    weight /= 2.0
  return weight

def get_top_track_ids():
  params = { 'limit': 50, 'offset': 0, 'time_range': 'medium_term' } # Last 6 months
  top_tracks = session['authorized_client'].get('me/top/tracks', **params).parsed['items']
  top_track_ids = [ x['id'] for x in top_tracks ]
  if not top_track_ids:
    raise NoListeningDataException
  return top_track_ids

def get_audio_features(track_ids):
  params = { 'ids': ','.join(track_ids) }
  return session['authorized_client'].get('audio-features', **params).parsed['audio_features']

def get_compass_values(track_audio_features, x_axis_key, y_axis_key):
  total_x_axis = 0
  total_y_axis = 0
  weight_sum = 0

  for track_num, track_features in enumerate(track_audio_features):
    weight = get_weight(track_num)
    total_x_axis += (track_features[x_axis_key] * weight)
    total_y_axis += (track_features[y_axis_key] * weight)
    weight_sum += weight

  # Weighted average (divide by the sum of all weights)
  mean_x_axis = convert_to_plot_range(total_x_axis / weight_sum)
  mean_y_axis = convert_to_plot_range(total_y_axis / weight_sum)

  return (mean_x_axis, mean_y_axis)
