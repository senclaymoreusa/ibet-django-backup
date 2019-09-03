import base64
import random
import hashlib
import logging
import requests
import json
import os
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from users.models import CustomUser
from utils.constants import *
from accounting.models import Transaction


def verify_user(request):
    if request.method == "POST":
        print("received post for verify/user")
        return JsonResponse({"msg": "hi"})


def authorize(request):
    if request.method == "POST":
        print("received post for authorize")
        return JsonResponse({"msg": "hi"})


def transfer(request):
    if request.method == "POST":
        print("received post for transfer")
        return JsonResponse({"msg": "hi"})


def cancel(request):
    if request.method == "POST":
        print("received post for cancel")
        return JsonResponse({"msg": "hi"})
