from django.shortcuts import render
from django.http import HttpResponse
from django.views import View, generic
from django.utils import timezone
from django.db import IntegrityError
from users.models import Game, CustomUser, Category, Config, NoticeMessage
from ..models import Transaction, ThirdParty, DepositChannel, WithdrawChannel, DepositAccessManagement, WithdrawAccessManagement
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes


from ..serializers import depositMethodSerialize, bankListSerialize,bankLimitsSerialize,submitDepositSerialize,submitPayoutSerialize, payoutTransactionSerialize,approvePayoutSerialize,depositThirdPartySerialize, payoutMethodSerialize,payoutBanklistSerialize,payoutBanklimitsSerialize
from django.conf import settings
import requests,json
import os
import datetime,time
import hmac
import hashlib 
import base64
import logging