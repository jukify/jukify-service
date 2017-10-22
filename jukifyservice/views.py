from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from jukifyservice.models import User
from jukifyservice.serializers import UserSerializer

import configparser

# import client tokens from configs file
configs = configparser.ConfigParser()
configs.read('jukifyservice/configs.ini')
MY_CLIENT_ID = configs['jukify']['client_id']
MY_CLIENT_SECRET = configs['jukify']['client_secret']
MY_REDIRECT_URI = configs['jukify']['redirect_uri']


def get_code(request, code):
    """
    Just a proof of concept
    """
    if request.method == 'GET':
        return JsonResponse({'code': code})
