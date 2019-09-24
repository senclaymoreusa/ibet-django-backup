from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import CustomUser, GameRequestsModel
from django.utils import timezone
import decimal
import xmltodict

class SAGetUserBalance(APIView):
    