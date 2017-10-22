from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from jukifyservice.models import User
from jukifyservice.serializers import UserSerializer

import configparser
import base64
import requests
import json

# import client tokens from configs file
configs = configparser.ConfigParser()
configs.read('jukifyservice/configs.ini')
CLIENT_ID = configs['jukify']['client_id']
CLIENT_SECRET = configs['jukify']['client_secret']
REDIRECT_URI = configs['jukify']['redirect_uri']

# spotify urls
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_API_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
SPOTIFY_API_VERSION = "v1"
SPOTIFY_API_URL = "%s/%s" % (SPOTIFY_API_BASE_URL, SPOTIFY_API_VERSION)


@csrf_exempt
def get_me(request):
    if request.method == 'POST':
        auth_header = get_auth(request)
        profile_data = request_to_api('/me', auth_header)
        return JsonResponse(profile_data, safe=False)


def get_auth(request):
    request_body = json.loads(request.body)
    code = request_body['code']

    body_params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    client_keys = "%s:%s" % (CLIENT_ID, CLIENT_SECRET)
    client_keys_base64 = base64.b64encode(client_keys.encode())

    header_params = {
        "Authorization": "Basic %s" % client_keys_base64
    }

    response = requests.post(SPOTIFY_API_TOKEN_URL,
                             data=body_params,
                             headers=header_params)

    # getting tokens from response
    response_json = json.loads(response.text)
    access_token = response_json['access_token']
    token_type = response_json['token_type']
    expires_in = response_json['expires_in']
    refresh_token = response_json['refresh_token']
    auth_header = {"Authorization": "Bearer %s" % access_token}

    return auth_header


def request_to_api(endpoint, auth_header):
    full_endpoint = "%s%s" % (SPOTIFY_API_URL, endpoint)
    response = requests.get(full_endpoint, headers=auth_header)
    return json.loads(response.text)
