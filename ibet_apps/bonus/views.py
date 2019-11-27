from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from bonus.models import *
from users.models import CustomUser
from games.models import Category
from utils.admin_helper import displayChoiceValue

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
import datetime
from django.utils import timezone
from django.db.models import Sum, Q
from django.db.models import Count

logger = logging.getLogger('django')

# Create your views here.
class BonusSearchView(View):

    # Returns a dictionary in JSON where the key is the PK of each bonus, and the value is the whole object
    # (containing all the requirements as a list)
    # This will also return bonuses that are NOT active.
    def get(self, request, *args, **kwargs):
        bonuses = {}
        result = {}
        bonus_all = Bonus.objects.all()

        try:
            request_type = request.GET.get('type')
            length = int(request.GET.get('length', 20))
            start = int(request.GET.get('start', 0))
            search_value = request.GET.get('search', None)
            order_column = int(request.GET.get('order[0][column]', -1))
            order = request.GET.get('order[0][dir]', None)
            bonus_type = int(request.GET.get('bonus_type', -1))
            bonus_status = int(request.GET.get('bonus_status', -1))

            if request_type == "adminBonusList":
                #  TOTAL ENTRIES
                total = bonus_all.count()

                bonus_filter = Q()

                # BONUS TYPE AND STATUS FILTER
                if bonus_type != -1:
                    bonus_filter &= Q(type=bonus_type)

                if bonus_status != -1:
                    bonus_filter &= Q(status=bonus_status)

                #  SEARCH BOX
                if search_value:
                    bonus_filter &= (Q(name__icontains=search_value) | Q(campaign__name__icontains=search_value))

                bonus_all = bonus_all.filter(bonus_filter)

                # START TIME SORTING
                count = bonus_all.count()
                if order_column:
                    if order == 'desc':
                        bonus_all = bonus_all.order_by('-start_time')[start:start + length]
                    else:
                        bonus_all = bonus_all.order_by('start_time')[start:start + length]
                else:
                    bonus_all = bonus_all[start:start + length]

                result['recordsTotal'] = total
                result['recordsFiltered'] = count

        except Exception as e:
            logger.error("Error getting request: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        # We iterate through all requirements and find all bonuses that they are attached to
        reqs = Requirement.objects.all()
        for req in reqs:
            if req.bonus not in bonus_all:
                continue
            bonus_data = serializers.serialize('json', [req.bonus])
            bonus_data = json.loads(bonus_data)
            bonus_data[0]['fields'] = displayChoiceValue(bonus_data[0]['fields'])
            req_data = serializers.serialize('json', [req])
            req_data = json.loads(req_data)[0]
            pk = bonus_data[0]['pk']

            if pk in bonuses:
                bonuses[pk]['requirements'].append(req_data)
            else:
                bonuses[pk] = bonus_data[0]['fields']
                bonuses[pk]['requirements'] = [req_data]

        # In rare cases, there could be bonuses that do not have any requirements
        for bonus in bonus_all:
            if str(bonus.pk) in bonuses.keys():
                continue
            bonus_left = serializers.serialize('json', [bonus])
            bonus_left = json.loads(bonus_left)
            bonuses[bonus_left[0]['pk']] = displayChoiceValue(bonus_left[0]['fields'])

        # Now that bonuses keep all the bonus objects. We need to join with the BonusCategory table to get
        # all the applicable categories for each bonus.
        for pk in bonuses.keys():
            for bc_obj in BonusCategory.objects.all():
                if str(bc_obj.bonus.pk) != pk:
                    continue
                bonus_obj = bonuses[pk]
                category_json = serializers.serialize('json', {bc_obj.category})
                category_json = json.loads(category_json)
                if 'categories' in bonus_obj.keys():
                    bonus_obj['categories'].append (category_json)
                else:
                    bonus_obj['categories'] = [category_json]

        # For each Bonus, we need to compute the 4 metrics over its history.
        # These are only for our admin backend.
        # DO NOT use them for frontend display.
        for pk in bonuses.keys():

            ###TODO: BELOW is NOT good design - as it requires hitting the database for 4 times.
            ###Instead, we should get all the data at once and compute the sums and counts in the memory.
            ###We should tune this if it turns out to be bad in performance testing.
            (ube_sum_issued, ube_count_issued, ube_sum_redeemed, ube_count_redeemed) = (
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_ISSUED).aggregate(Sum('amount'))['amount__sum'] or 0,
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_ISSUED).aggregate(Count('amount'))['amount__count'],
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_REDEEMED).aggregate(Sum('amount'))['amount__sum'] or 0,
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_REDEEMED).aggregate(Count('amount'))['amount__count']
            )

            bonuses[pk]['total_amount_issued'] = ube_sum_issued
            bonuses[pk]['total_count_issued'] = ube_count_issued
            bonuses[pk]['total_amount_redeemed'] = ube_sum_redeemed
            bonuses[pk]['total_count_redeemed'] = ube_count_redeemed

        result['data'] = list(bonuses.values())
        return HttpResponse(json.dumps(result), content_type='application/json')


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

            # We need to join with the BonusCategory table to get all the applicable categories for this bonus.
            for bc_obj in BonusCategory.objects.all():
                if str(bc_obj.bonus.pk) != bonus_pk:
                    continue
                category_json = serializers.serialize('json', {bc_obj.category})
                category_json = json.loads(category_json)
                if 'categories' in bonus_data.keys():
                    bonus_data['categories'].append(category_json)
                else:
                    bonus_data['categories'] = [category_json]

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
                    currency = req_data['currency']

                    ## TODO: Need to deal with campaign if that's decided to be a P0 feature
                )
                bonus_obj.save()
            except Exception as e:
                logger.error("Error saving new Bonus object: ", e)
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

            if 'requirements' in req_data.keys():
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

            if 'categories' in req_data.keys():
                try:
                    categories = req_data['categories']
                    for cat in categories:
                        cat_pk = cat[0]['pk']
                        bc_obj = BonusCategory (
                            bonus = bonus_obj,
                            category = Category.objects.get(pk=cat_pk),
                        )
                        bc_obj.save()

                except Exception as e:
                    logger.error("Error saving new BonusCategory object: ", e)
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        ## I don't think we should allow all the fields of a bonus to be updated
        ## We also assume we cannot update requirements or categories
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


class UserBonusEventView(View):

    # Given a user and a bonus, returns all the events, sorted by timestamp
    def get(self, request, *arg, **kwargs):

        try:
            bonus_pk = request.GET.get('bonus')
            user_pk = request.GET.get('user')

            events = UserBonusEvent.objects.filter(bonus=bonus_pk,owner=user_pk).order_by('-timestamp')
            response = serializers.serialize('json', events)
            response = json.loads(response)

        except Exception as e:
            logger.error("Error getting UserBonusEvent objects: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(json.dumps(response), content_type='application/json', status=status.HTTP_200_OK)

    # Creates a NEW event between a User and Bonus.
    # You can never "update" an event that already happened between a User and Bonus.
    # ... and let's make this simple: the frontend can just pass the fields in the QueryDict instead of constructiing
    # the real objects
    @transaction.atomic
    def post(self, request, *arg, **kwargs):

        try:
            bonus_pk = request.GET.get('bonus')
            user_pk = request.GET.get('user')
            delivered_by = request.GET.get('delivered_by')
            bonus_obj = Bonus.objects.get(pk=bonus_pk)
            cuser_obj = CustomUser.objects.get(pk=user_pk)
            delivered_by_obj = CustomUser.objects.get(pk=delivered_by)

        except Exception as e:
            logger.error("Error getting Bonus or User object: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        try:
            event_obj = UserBonusEvent (
                owner = cuser_obj,
                bonus = bonus_obj,
                timestamp = timezone.now(),
                delivered_by = delivered_by_obj,
                status = request.GET.get('status'),
                notes = request.GET.get('notes'),
                amount=request.GET.get('amount'),

            )
            event_obj.save()
        except Exception as e:
            logger.error("Error saving new UserBonusEvent object: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(status=status.HTTP_200_OK)
