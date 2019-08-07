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
from ..models import Transaction