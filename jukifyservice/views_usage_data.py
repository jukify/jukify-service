""" Handles users' usage data fetching

..  _Spotify Web API
    https://developer.spotify.com/web-api/
"""

from jukifyservice.views import *


def get_users_saved_tracks(request, user_id):
    """ Retrieves user's saved tracks and saves to our database

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
            data = get_usage_data(user_id, track['id'])
            if data == None:
                data = UsageData(
                    user_id=user_id, track_id=track['id'], rating=1)
            else:
                data.rating += 1
            data.save()

    next_page = saved_tracks['next']

    if next_page != None:
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['offset'] = str(saved_tracks['offset'] + saved_tracks['limit'])
        return get_users_saved_tracks(request, user_id)

    return HttpResponse()
