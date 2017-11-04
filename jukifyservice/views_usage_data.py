""" Handles users' usage data fetching

..  _Spotify Web API
    https://developer.spotify.com/web-api/
"""

from jukifyservice.views import *


def save_usage_data(user_id, track_id):
    """ Utility function for saving usage data
    """
    data = get_usage_data(user_id, track_id)
    if data == None:
        data = UsageData(user_id=user_id, track_id=track_id, rating=1)
    else:
        data.rating += 1
    data.save()


def get_users_saved_tracks(request, user_id):
    """ Retrieves user's saved tracks and saves them

    ..  _Get a User’s Saved Tracks endpoint
        https://developer.spotify.com/web-api/get-users-saved-tracks/
    """
    limit = request.GET['limit']
    offset = request.GET['offset']
    market = request.GET['market']
    endpoint = '/me/tracks?limit=' + limit + \
        '&offset=' + offset + '&market=' + market
    saved_tracks_str = json.dumps(get_from_user_api(endpoint, user_id))
    saved_tracks = json.loads(saved_tracks_str)

    for track in saved_tracks['items']:
        track = track['track']
        if track['is_playable']:
            save_usage_data(user_id, track['id'])

    next_page = saved_tracks['next']

    if next_page != None:
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['offset'] = str(
            saved_tracks['offset'] + saved_tracks['limit'])
        return get_users_saved_tracks(request, user_id)

    return HttpResponse()


def get_top_artists_tracks(request, user_id):
    """Retrieves user's top 10 artists and saves their top 5 tracks

    ..  _Get a User’s Top Artists and Tracks endpoint
        https://developer.spotify.com/web-api/get-users-top-artists-and-tracks/

    ..  _Get an Artist’s Top Tracks endpoint
        https://developer.spotify.com/web-api/get-artists-top-tracks/
    """
    endpoint = '/me/top/artists?limit=10'
    top_artists_str = json.dumps(get_from_user_api(endpoint, user_id))
    top_artists = json.loads(top_artists_str)

    for artist in top_artists['items']:
        artist_endpoint = '/artists/' + artist['id'] + '/top-tracks?country=BR'
        top_tracks_str = json.dumps(
            get_from_user_api(artist_endpoint, user_id))
        top_tracks = json.loads(top_tracks_str)

        for track in top_tracks['tracks'][:5]:
            save_usage_data(user_id, track['id'])

    return HttpResponse()
