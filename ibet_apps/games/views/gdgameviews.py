from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from users.models import CustomUser
from  games.models import *
from zeep import Client

logger = logging.getLogger('django')

client = Client(wsdl='https://ibet-web-dev.claymoreeuro.com/production.svc?wsdl')
#print(client.service.Add(12,13))