from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from jukifyservice.models import User
from jukifyservice.serializers import UserSerializer

def get_code(request, code):
    """
    Just a proof of concept
    """
    if request.method == 'GET':
        return JsonResponse({'foo': code})
