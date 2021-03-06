from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from jukifyservice.models import User, Group, Membership, Track, Playlist, PlaylistTrack, UsageData
from jukifyservice.serializers import UserSerializer


from datetime import datetime
import base64
import requests
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# import client tokens from environment variables
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# spotify urls
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_API_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
SPOTIFY_API_VERSION = "v1"
SPOTIFY_API_URL = "%s/%s" % (SPOTIFY_API_BASE_URL, SPOTIFY_API_VERSION)


# endpoints

@csrf_exempt
def login(request):
    if request.method == 'POST':
        user_tokens = auth(request)

        access_token = user_tokens['access_token']
        token_type = user_tokens['token_type']
        expires_in = user_tokens['expires_in']
        refresh_token = user_tokens['refresh_token']

        auth_header = get_auth_header(access_token)
        me = get_from_api('/me', auth_header)

        user = User(
            id=me['id'],
            api_endpoint=me['href'],
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            last_logged_at=datetime.now(),
            display_name=me['display_name']
        )

        user.save()

        return JsonResponse(me, safe=False)


# user endpoints

def list_users(request):
    if request.method == 'GET':
        users = [{'id': u.id, 'name': u.display_name} for u in User.objects.all()]
        return JsonResponse(users, safe=False)


def list_groups_from_user(request, user_id):
    if request.method == 'GET':
        user = get_user(user_id)

        if user != None:
            groups = [g.id for g in user.group_set.all()]
            return JsonResponse(groups, safe=False)

        return HttpResponseBadRequest()


# group endpoints

@csrf_exempt
def groups(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        creator_id = body['creator_id']
        user = get_user(creator_id)

        if user != None:
            group = Group()
            group.save()
            membership = Membership(user=user, group=group)
            membership.save()
            return JsonResponse({"group_id": group.id})

        return HttpResponseBadRequest()

    elif request.method == 'DELETE':
        body = json.loads(request.body)
        group_id = body['group_id']
        group = get_group_by_id(group_id)

        if group != None:
            group.delete()
            return HttpResponse()

        return HttpResponseBadRequest()


@csrf_exempt
def group_users(request, group_id):
    if request.method == 'GET':
        group = get_group_by_id(group_id)

        if group != None:
            users = [{ 'id': u.id, 'name': u.display_name } for u in group.users.all()]
            return JsonResponse(users, safe=False)

    elif request.method == 'POST':
        body = json.loads(request.body)
        user_id = body['user_id']
        user = get_user(user_id)
        group = get_group_by_id(group_id)

        if user != None and group != None:
            membership = Membership(user=user, group=group)
            membership.save()
            users = [{'id': u.id, 'name': u.display_name} for u in group.users.all()]
            return JsonResponse({"group": users}, safe=False)

    elif request.method == 'DELETE':
        body = json.loads(request.body)
        user_id = body['user_id']
        user = get_user(user_id)
        group = get_group_by_id(group_id)

        if user != None and group != None:
            membership = Membership.objects.get(user=user, group=group)
            membership.delete()
            if not group.users.all():
                group.delete()
                return JsonResponse({"group": []})
            users = [{'id': u.id, 'name': u.display_name} for u in group.users.all()]
            return JsonResponse({"group": users}, safe=False)

    return HttpResponseBadRequest()


def group_recommendations(request, group_id):
    if request.method == 'GET':
        return JsonResponse({"recommendations": "Pink Floyd"})


@csrf_exempt
def group_playlist(request, group_id):
    if request.method == 'GET':
        group = get_group_by_id(group_id)
        if group != None:
            playlist = get_playlist_by_group(group)
            if playlist != None:
                return JsonResponse({"playlist_url": playlist.url})
            logger.debug('No playlist found for group_id=', group_id)
            return JsonResponse({}, safe=False)
        else:
            logger.debug('No group found for group_id=', group_id)

    elif request.method == 'POST':
        group = get_group_by_id(group_id)
        if group != None:
            body = json.loads(request.body)
            user_id = body['user_id']
            user = get_user(user_id)
            if user != None:
                tracks = body['tracks']
                playlist_id = create_playlist(user_id, group_id, tracks)
                if playlist_id != None:
                    return JsonResponse({"playlist_id": playlist_id})
                else:
                    logger.info("Playlist not created for group=%s" % group_id)
            else:
                logger.info('No user found for user_id=', user_id)
        else:
            logger.info('No group found for group_id=', group_id)
    
    return HttpResponseBadRequest()


# auth methods

def auth(request):
    request_body = json.loads(request.body)
    code = request_body['code']
    redirect_uri = request_body['redirect_uri']

    body_params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    response = post_to_token(body_params, get_client_header())

    user_tokens = json.loads(response.text)
    return user_tokens


def refresh(user_id):
    user = get_user(user_id)

    if user != None:
        body_params = {
            "grant_type": "refresh_token",
            "refresh_token": user.refresh_token
        }

        response = post_to_token(body_params, get_client_header())
        user_tokens = json.loads(response.text)
        user.access_token = user_tokens['access_token']
        user.expires_in = user_tokens['expires_in']
        user.save()


def get_client_header():
    client_keys = "%s:%s" % (CLIENT_ID, CLIENT_SECRET)
    client_keys_base64 = base64.b64encode(client_keys.encode()).decode()

    return {"Authorization": "Basic %s" % client_keys_base64}


def get_auth_header(access_token):
    return {"Authorization": "Bearer %s" % access_token}


# auxiliar methods

def post_to_token(body, headers):
    return requests.post(SPOTIFY_API_TOKEN_URL,
                         data=body,
                         headers=headers)


def create_playlist(user_id, group_id, tracks):
    user = get_user(user_id)
    group = get_group_by_id(group_id)
    if user != None and group != None:
        endpoint = SPOTIFY_API_URL + '/users/%s/playlists' % user_id
        body = "{\"name\": \"jukify-group-%s\", \"description\": \"Playlist generated by Jukify app - Check us out at jukify.us\"}" % group_id
        refresh(user_id)
        headers = get_auth_header(user.access_token)
        headers['Content-Type'] = 'application/json'
        response = requests.post(endpoint, data=body, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            response = json.loads(response.text)
            playlist_id = response['id']
            logger.info("Created playlist=%s for user=%s, group=%s" % (playlist_id, user_id, group_id))
            playlist_url = response['external_urls']['spotify'] if (
                'external_urls' in response and 'spotify' in response['external_urls']) else ''
            existing_playlist = get_playlist_by_group(group)
            if existing_playlist != None:
                logger.info("Removing playlist=%s from group=%s" % (existing_playlist.id, group_id))
                existing_playlist.delete()
            playlist = Playlist(id=playlist_id, group=group, url=playlist_url)
            playlist.save()
            logger.info("Saved playlist=%s, url=%s" % (playlist_id, playlist_url))
            endpoint += '/%s/tracks' % playlist_id
            uris = json.dumps(['spotify:track:%s' % track_id for track_id in tracks])
            refresh(user_id)
            headers = get_auth_header(user.access_token)
            headers['Content-Type'] = 'application/json'
            body = "{\"uris\": " + uris + "}"
            logger.info("Adding tracks for playlist=%s" % playlist_id)
            response = requests.post(endpoint, data=body, headers=headers)
            if response.status_code != 201:
                logger.info("Error adding tracks to playlist=%s" % playlist_id)
            return playlist_id
        else:
            logger.info("Error creating playlist for user=%s, group=%s" % (user_id, group_id))
    elif user == None:
        logger.info("User=%s does not exist" % user_id)
    else:
        logger.info("Group=%s does not exist" % group_id)
    return None


def get_from_user_api(endpoint, user_id):
    refresh(user_id)
    user = get_user(user_id)
    if user != None:
        auth_header = get_auth_header(user.access_token)
        return get_from_api(endpoint, auth_header)
    return None


def get_from_api(endpoint, auth_header):
    full_endpoint = "%s%s" % (SPOTIFY_API_URL, endpoint)
    response = requests.get(full_endpoint, headers=auth_header)
    return json.loads(response.text)


def get_user(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None
    return user


def get_group_by_id(group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        group = None
    return group


def get_playlist_by_group(group):
    try:
        playlist = Playlist.objects.get(group=group)
    except Playlist.DoesNotExist:
        playlist = None
    return playlist


def get_usage_data(user_id, track_id):
    try:
        data = UsageData.objects.get(user_id=user_id, track_id=track_id)
    except UsageData.DoesNotExist:
        data = None
    return data
