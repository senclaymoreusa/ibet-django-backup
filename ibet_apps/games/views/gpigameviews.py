from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction, IntegrityError
from users.models import CustomUser
from accounting.models import * 
import simplejson as json
from decimal import Decimal
import requests
from utils.constants import *
import random
import hashlib 
import logging
import datetime
from datetime import date
from django.utils import timezone
import uuid
from  games.models import *
import json
import time
import urllib
# from background_task import background
import redis
from utils.redisClient import RedisClient
from utils.redisHelper import RedisHelper

from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad
from games.helper import *
from utils.aws_helper import getThirdPartyKeys

logger = logging.getLogger('django')

import base64
