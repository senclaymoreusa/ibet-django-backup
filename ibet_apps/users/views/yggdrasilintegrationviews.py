from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import CustomUser, GameRequestsModel 
import simplejson as json
import xmltodict
import decimal

class YggdrasilAPI(APIView):

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):

        Status = status.HTTP_200_OK

        return Response(status=Status)