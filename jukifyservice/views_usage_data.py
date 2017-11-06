""" Handles users' usage data fetching

..  _Spotify Web API
    https://developer.spotify.com/web-api/
"""

from jukifyservice.views import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" [UsageData] ")


def save_usage_data(user_id, track_id):
    """ Utility function for saving usage data
    """
    data = get_usage_data(user_id, track_id)
    if data == None:
        data = UsageData(user_id=user_id, track_id=track_id, rating=1)
    else:
        data.rating += 1
    data.save()


def dict_to_json(d):
    """ Utility function for converting a dict to a json object
    """
    d_str = json.dumps(d)
    return json.loads(d_str)


def save_saved_tracks(request, user_id):
    """ Retrieves user's saved tracks and saves them

    ..  _Get a User’s Saved Tracks endpoint
        https://developer.spotify.com/web-api/get-users-saved-tracks/
    """
    limit = request.GET['limit']
    offset = request.GET['offset']
    market = request.GET['market']

    logger.info("Fetching saved tracks for user_id=%s, limit=%s, offset=%s",
                user_id, limit, offset)

    endpoint = '/me/tracks?limit=' + limit + \
        '&offset=' + offset + '&market=' + market
    saved_tracks_str = json.dumps(get_from_user_api(endpoint, user_id))
    saved_tracks = json.loads(saved_tracks_str)

    for track in saved_tracks['items']:
        track = track['track']
        if 'is_playable' in track and track['is_playable']:
            save_usage_data(user_id, track['id'])

    next_page = saved_tracks['next']

    if next_page != None:
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['offset'] = str(
            saved_tracks['offset'] + saved_tracks['limit'])
        save_saved_tracks(request, user_id)

    return HttpResponse()


def save_top_artists_tracks(request, user_id):
    """Retrieves user's top 10 artists and saves their top 5 tracks

    ..  _Get a User’s Top Artists and Tracks endpoint
        https://developer.spotify.com/web-api/get-users-top-artists-and-tracks/

    ..  _Get an Artist’s Top Tracks endpoint
        https://developer.spotify.com/web-api/get-artists-top-tracks/
    """
    endpoint = '/me/top/artists?limit=10'
    top_artists_str = json.dumps(get_from_user_api(endpoint, user_id))
    top_artists = json.loads(top_artists_str)

    logger.info("Fetching top artists for user_id=%s", user_id)

    for artist in top_artists['items']:
        artist_endpoint = '/artists/' + artist['id'] + '/top-tracks?country=BR'
        top_tracks_str = json.dumps(
            get_from_user_api(artist_endpoint, user_id))
        top_tracks = json.loads(top_tracks_str)

        for track in top_tracks['tracks'][:5]:
            save_usage_data(user_id, track['id'])

    return HttpResponse()


def save_top_tracks(request, user_id):
    """Saves user's top tracks

    ..  _Get a User’s Top Artists and Tracks endpoint
        https://developer.spotify.com/web-api/get-users-top-artists-and-tracks/
    """
    limit = request.GET['limit']
    offset = request.GET['offset']

    logger.info("Fetching top tracks for user_id=%s, limit=%s, offset=%s",
                user_id, limit, offset)

    endpoint = '/me/top/tracks?limit=' + limit + '&offset=' + offset
    top_tracks_str = json.dumps(get_from_user_api(endpoint, user_id))
    top_tracks = json.loads(top_tracks_str)

    for track in top_tracks['items']:
        if 'is_playable' in track and track['is_playable']:
            save_usage_data(user_id, track['id'])

    next_page = top_tracks['next']

    if next_page != None:
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['offset'] = str(top_tracks['offset'] + top_tracks['limit'])
        save_top_tracks(request, user_id)

    return HttpResponse()


def save_playlists(request, user_id):
    """ Fetch the user's playlists and saves their tracks

    ..  _Get a List of Current User’s Playlists endpoint
        https://developer.spotify.com/web-api/get-a-list-of-current-users-playlists/
    """
    limit = request.GET['limit']
    offset = request.GET['offset']

    logger.info("Fetching playlists for user_id=%s, limit=%s, offset=%s",
                user_id, limit, offset)

    endpoint = '/me/playlists?limit=' + limit + '&offset=' + offset
    playlists = dict_to_json(get_from_user_api(endpoint, user_id))

    for playlist in playlists['items']:
        owner_id = playlist['owner']['id']
        save_tracks(user_id, owner_id, playlist['id'])

    next_page = playlists['next']

    if next_page != None:
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['offset'] = str(playlists['offset'] + playlists['limit'])
        save_playlists(request, user_id)

    return HttpResponse()


def save_tracks(user_id, owner_id, playlist_id, offset='0'):
    """ Saves a playlist's tracks

    ..  _Get a Playlist’s Tracks endpoint
        https://developer.spotify.com/web-api/get-playlists-tracks/
    """
    logger.info("Fetching tracks from playlist_id=%s for user_id=%s, offset=%s",
                playlist_id, user_id, offset)

    endpoint = '/users/' + owner_id + '/playlists/' + playlist_id + \
        '/tracks?market=BR&fields=limit,offset,next,items(track(id,name,is_playable))&offset=' + offset
    tracks = dict_to_json(get_from_user_api(endpoint, user_id))

    for item in tracks['items']:
        track = item['track']
        if 'is_playable' in track and track['is_playable']:
            save_usage_data(user_id, track['id'])

    next_page = tracks['next']

    if next_page != None:
        offset = str(tracks['offset'] + tracks['limit'])
        save_tracks(user_id, owner_id, playlist_id, offset)
