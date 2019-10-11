from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from bonus.models import *

from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.
import logging
from django.core import serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, HttpResponse
import simplejson as json
from utils.constants import *
from django.db import transaction
from rest_framework import status


logger = logging.getLogger('django')

# Create your views here.

class BonusSearchView(View):

    # Returns a dictionary in JSON where the key is the PK of each bonus, and the value is the whole object
    # (containing all the requirements as a list)
    # This will also return bonuses that are NOT active.
    def get(self, request, *args, **kwargs):

        bonuses = {}

        # We iterate through all requirements and find all bonuses that they are attached to
        reqs = Requirement.objects.all()
        for req in reqs:

            bonus_data = serializers.serialize('json', [req.bonus])
            bonus_data = json.loads(bonus_data)
            req_data = serializers.serialize('json', [req])
            req_data = json.loads(req_data)[0]

            pk = bonus_data[0]['pk']
            if pk in bonuses:
                bonuses[pk]['requirements'].append(req_data)
            else:
                bonuses[pk] = bonus_data[0]['fields']
                bonuses[pk]['requirements'] = [req_data]

        # In rare cases, there could be bonuses that do not have any requirements
        bonus_all = Bonus.objects.all()
        for bonus in bonus_all:
            if str(bonus.pk) in bonuses.keys():
                continue
            bonus_left = serializers.serialize('json', [bonus])
            bonus_left = json.loads(bonus_left)
            bonuses[bonus_left[0]['pk']] = bonus_left[0]['fields']

        return HttpResponse(json.dumps(bonuses), content_type='application/json')

class BonusView(View):

    # Returns a Bonus object in JSON (containing all the requirements as a list)
    def get(self, request, *arg, **kwargs):

        try:
            bonus_pk = self.kwargs.get('pk')
            bonus = Bonus.objects.get(pk=bonus_pk)
            bonus_data = serializers.serialize('json', {bonus})
            bonus_data = json.loads(bonus_data)[0]['fields']

            # We need to iterate through all the requirements as we do not have the mapping,
            # but that should be fine performance-wise, as we don't have too many bonuses or requirements anyway.
            reqs = Requirement.objects.all()
            for req in reqs:

                if bonus_pk != str(req.bonus.pk):
                    continue

                req_data = serializers.serialize('json', [req])
                req_data = json.loads(req_data)[0]
                if 'requirements' in bonus_data.keys():
                    bonus_data['requirements'].append(req_data)
                else:
                    bonus_data['requirements'] = [req_data]

        except Exception as e:
            logger.error("Error getting Bonus object: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(json.dumps(bonus_data), content_type='application/json', status=status.HTTP_200_OK)

    # Updates the Bonus object if the pk is given, and creates a new Bonus object otherwise.
    @transaction.atomic
    def post(self, request, *arg, **kwargs):

        bonus_pk = self.kwargs.get('pk')
        try:
            bonus = Bonus.objects.get(pk=bonus_pk)
        except:
            bonus = None

        req_data = json.loads(request.body)

        if bonus is None:

            try:
                bonus_obj = Bonus (
                    name = req_data['name'],
                    description = req_data['description'],
                    start_time = req_data['start_time'],
                    end_time = req_data['end_time'],
                    expiration_days = req_data['expiration_days'],
                    countries = req_data['countries'],
                    amount = req_data['amount'],
                    percentage = req_data['percentage'],
                    coupon_code = req_data['coupon_code'],
                    affiliate_limit = req_data['affiliate_limit'],
                    release_type = req_data['release_type'],
                    image_s3 = req_data['image_s3'],

                    status = req_data['status'],
                    is_free_bid = req_data['is_free_bid'],
                    type = req_data['type'],

                    ## TODO: Need to deal with campaign if that's decided to be a P0 feature
                )
                bonus_obj.save()
            except Exception as e:
                logger.error("Error saving new Bonus object: ", e)
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

            try:
                requirements = req_data['requirements']
                for req in requirements:

                    req_new = Requirement (
                        field_name = req['field_name'],
                        aggregate_method = req['aggregate_method'],
                        time_limit = req['time_limit'],
                        turnover_multiplier = req['turnover_multiplier'],
                        amount_threshold = req['amount_threshold'],
                        bonus = bonus_obj,
                    )
                    req_new.save()
            except Exception as e:
                logger.error("Error saving new Requirement object: ", e)
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        ## I don't think we should allow all the fields of a bonus to be updated
        ## We also assume we cannot update requirements
        else:

            try:
                bonus.name = req_data['name']
                bonus.description = req_data['description']
                bonus.start_time = req_data['start_time']
                bonus.end_time = req_data['end_time']
                bonus.expiration_days = req_data['expiration_days']
                bonus.countries = req_data['countries']
                bonus.amount = req_data['amount']
                bonus.percentage = req_data['percentage']
                bonus.coupon_code = req_data['coupon_code']
                bonus.affiliate_limit = req_data['affiliate_limit']
                bonus.release_type = req_data['release_type']
                bonus.image_s3 = req_data['image_s3']
                bonus.status = req_data['status'],

                bonus.save()
            except Exception as e:
                logger.error("Error updating Bonus object: ", e)
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(status=status.HTTP_200_OK)

