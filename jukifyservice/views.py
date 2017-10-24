from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from jukifyservice.models import User
from jukifyservice.serializers import UserSerializer

from datetime import datetime
import base64
import requests
import json
import os

# import client tokens from environment variables
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

print(CLIENT_ID, CLIENT_SECRET)

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

        print(user_tokens)
        access_token = user_tokens['access_token']
        token_type = user_tokens['token_type']
        expires_in = user_tokens['expires_in']
        refresh_token = user_tokens['refresh_token']

        auth_header = get_auth_header(access_token)
        me = request_to_api('/me', auth_header)

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


def list_users(request):
    if request.method == 'GET':
        users = [u.id for u in User.objects.all()]
        return JsonResponse(users, safe=False)


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

    print(body_params)
    response = post_to_token(body_params, get_client_header())

    print(response)
    user_tokens = json.loads(response.text)
    return user_tokens


def refresh(user_id):
    user = User.objects.filter(id=user_id)[0]

    body_params = {
        "grant_type": "refresh_token",
        "refresh_token": user.refresh_token
    }

    response = post_to_token(body_params, get_client_header())

    user_tokens = json.loads(response.text)
    return user_tokens


def get_client_header():
    client_keys = "%s:%s" % (CLIENT_ID, CLIENT_SECRET)
    client_keys_base64 = base64.b64encode(client_keys.encode()).decode()

    return {"Authorization": "Basic %s" % client_keys_base64}


def get_auth_header(access_token):
    return {"Authorization": "Bearer %s" % access_token}


# auxiliar methods

def post_to_token(body, headers):
    print(headers)
    return requests.post(SPOTIFY_API_TOKEN_URL,
                         data=body,
                         headers=headers)


def request_to_api(endpoint, auth_header):
    full_endpoint = "%s%s" % (SPOTIFY_API_URL, endpoint)
    response = requests.get(full_endpoint, headers=auth_header)
    return json.loads(response.text)
