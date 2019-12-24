import sys

from django.shortcuts import render
from rest_framework.views import APIView
from django.views import View
from bonus.models import *
from users.models import CustomUser
from games.models import Category
from utils.admin_helper import bonusValueToKey, dateToDatetime, BONUS_TYPE_VALUE_DICT, BONUS_DELIVERY_VALUE_DICT, \
    BONUS_GAME_CATEGORY, ubeValueToKey, streamingExport

from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.
import logging
from django.core import serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import simplejson as json
from utils.constants import *
from django.db import transaction, IntegrityError
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
            bonus_data[0]['fields'] = bonusValueToKey(bonus_data[0]['fields'])
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
            bonuses[bonus_left[0]['pk']] = bonusValueToKey(bonus_left[0]['fields'])

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
                    bonus_obj['categories'].append(category_json)
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
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_ISSUED).aggregate(Sum('amount'))[
                    'amount__sum'] or 0,
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_ISSUED).aggregate(Count('amount'))[
                    'amount__count'],
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_REDEEMED).aggregate(Sum('amount'))[
                    'amount__sum'] or 0,
                UserBonusEvent.objects.filter(bonus=pk, status=BONUS_REDEEMED).aggregate(Count('amount'))[
                    'amount__count']
            )

            bonuses[pk]['total_amount_issued'] = ube_sum_issued
            bonuses[pk]['total_count_issued'] = ube_count_issued
            bonuses[pk]['total_amount_redeemed'] = ube_sum_redeemed
            bonuses[pk]['total_count_redeemed'] = ube_count_redeemed

        result['data'] = list(bonuses.values())

        if request.GET.get('export'):
            export_title = json.loads(request.GET.get('tableHead'))
            bonus_records_export = [export_title]
            for value in bonuses.values():
                bonus_records_export.append([value['name'],
                                             value['type'],
                                             value['total_amount_issued'],
                                             value['total_count_issued'],
                                             value['total_amount_redeemed'],
                                             value['total_count_redeemed'],
                                             value['start_time'],
                                             value['end_time'],
                                             value['status']])

            return streamingExport(bonus_records_export, "Bonus Records")

        return HttpResponse(json.dumps(result), content_type='application/json')


class BonusView(View):

    # Returns a Bonus object in JSON (containing all the requirements as a list)
    def get(self, request, *arg, **kwargs):

        try:
            bonus_name = self.kwargs.get('name')
            bonus = Bonus.objects.get(name=bonus_name)
            bonus_data = serializers.serialize('json', {bonus})
            bonus_data = json.loads(bonus_data)[0]['fields']

            # We need to iterate through all the requirements as we do not have the mapping,
            # but that should be fine performance-wise, as we don't have too many bonuses or requirements anyway.
            reqs = Requirement.objects.all()
            for req in reqs:

                if bonus_name != str(req.bonus.name):
                    continue

                req_data = serializers.serialize('json', [req])
                req_data = json.loads(req_data)[0]
                if 'requirements' in bonus_data.keys():
                    bonus_data['requirements'].append(req_data)
                else:
                    bonus_data['requirements'] = [req_data]

            # We need to join with the BonusCategory table to get all the applicable categories for this bonus.
            for bc_obj in BonusCategory.objects.all():
                if str(bc_obj.bonus.name) != bonus_name:
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
    def post(self, request, *arg, **kwargs):

        bonus_name = self.kwargs.get('name')
        try:
            bonus = Bonus.objects.get(name=bonus_name)
        except:
            bonus = None

        try:
            req_data = request.POST.get("bonusDict")
            req_data = json.loads(req_data)
        except Exception as e:
            logger.error("Error getting new bonus details " + str(e))
            response = JsonResponse({"error": "Error getting new bonus details"})
            response.status_code = 400
            return response

        try:
            if bonus is None:
                with transaction.atomic():
                    type = req_data.get('type')
                    if type == "triggered":
                        type = req_data.get('trigger_type')
                    type = BONUS_TYPE_VALUE_DICT.get(type)

                    bonus_amount_list = req_data.get('bonus_amount_list')

                    max_user_amount = req_data.get('max_user_amount')
                    max_amount = req_data.get('max_target_user_amount')

                    if max_user_amount:
                        max_user_amount = float(max_user_amount)

                    if max_amount:
                        max_amount = float(max_amount)

                    is_tiered = False
                    parent_bonus = None
                    bonus_number = len(bonus_amount_list)
                    # tiered bonus needs one more parent bonus
                    if bonus_number > 1:
                        is_tiered = True
                        bonus_number += 1

                    for i in range(0, bonus_number):
                        bonus_obj = Bonus(
                            name=req_data.get('name'),
                            description=req_data.get('description'),
                            start_time=dateToDatetime(req_data.get('start_time')),
                            end_time=dateToDatetime(req_data.get('end_time')),
                            expiration_days=req_data.get('expiration_days'),
                            countries=req_data.get('countries'),
                            coupon_code=req_data.get('coupon_code'),
                            affiliate_limit=req_data.get('affiliate_limit'),
                            image_s3=req_data.get('image_s3'),
                            status=int(req_data.get('status')),
                            is_free_bid='free-spin' in req_data.get('master_types') or 'free-bet' in req_data.get(
                                'master_types'),
                            type=type,
                            currency=req_data.get('currency') or 0,
                            issued=req_data.get('issued'),
                            max_daily_times=int(req_data.get('max_daily_times')),
                            max_total_times=int(req_data.get('max_total_times')),
                            max_relevant_times=int(req_data.get('max_associated_accounts')),
                            max_users=int(req_data.get('max_user')),
                            max_user_amount=max_user_amount,  # None is unlimited
                            max_amount=max_amount,  # None is unlimited
                            delivery=BONUS_DELIVERY_VALUE_DICT.get(req_data.get('delivery_method')),
                            ## TODO: Need to deal with campaign if that's decided to be a P0 feature
                        )

                        # assign amount and parent
                        # if tiered bonus, create parent bonus without amount or percentage
                        curr_idx = i
                        if is_tiered:
                            if i == 0:
                                parent_bonus = bonus_obj
                            else:
                                curr_idx = i - 1
                                bonus_obj.name = bonus_obj.name + ' ' + str(i)
                                bonus_obj.parent = parent_bonus

                        if 'bonus_amount' in bonus_amount_list[curr_idx].keys():
                            bonus_obj.amount = float(bonus_amount_list[curr_idx]['bonus_amount'])
                        elif 'bonus_percentage' in bonus_amount_list[curr_idx].keys():
                            bonus_obj.percentage = float(bonus_amount_list[curr_idx]['bonus_percentage'])

                        bonus_obj.save()
                        logger.info("Create a new bonus " + str(bonus_obj.name))

                        # for turnover bonus, wager requirement list length is 1
                        if req_data.get('trigger_type') == 'turnover':
                            curr_idx = 0

                        # skip add requirements for parent bonus
                        if 'requirements' in req_data.keys() and (not is_tiered or i != 0):
                            requirements = req_data['requirements']

                            must_have = requirements.get('must_have')
                            aggregate_method = requirements['aggregate_method']
                            time_limit = None
                            if requirements['time_limit']:
                                time_limit = int(requirements.get('time_limit'))
                            if must_have:
                                for req in must_have:
                                    must_have_req = Requirement(
                                        bonus=bonus_obj,
                                        must_have=int(req)
                                    )
                                    must_have_req.save()
                                    logger.info("Create a new must have Requirement for " + str(bonus_obj.name))
                            # add wager requirements
                            wager_multiple = requirements.get('wager_multiple')
                            wager_dict = wager_multiple[curr_idx]

                            # this bonus has no wager requirements on this product, and the bonus money cannot be
                            # applied on this product
                            for wager in wager_dict:
                                wager_cates = BONUS_GAME_CATEGORY[wager]
                                amount_threshold = 0
                                if 'amount_threshold' in bonus_amount_list[curr_idx].keys():
                                    amount_threshold = bonus_amount_list[curr_idx]['amount_threshold']

                                if float(wager_dict[wager]) == -1:
                                    continue
                                wager_req = Requirement(
                                    aggregate_method=aggregate_method,
                                    time_limit=time_limit,
                                    turnover_multiplier=int(wager_dict[wager]),
                                    amount_threshold=amount_threshold,
                                    bonus=bonus_obj,
                                )

                                wager_req.save()
                                logger.info("Create a new wager Requirement for " + str(bonus_obj.name))
                                # add requirement category and bonus category

                                for cate in wager_cates:
                                    wager_cate_obj = Category.objects.get(name=cate)

                                    rc_obj = RequirementCategory(
                                        requirement=wager_req,
                                        category=wager_cate_obj
                                    )
                                    rc_obj.save()
                                    logger.info("Create a new RequirementCategory for " + str(bonus_obj.name))

                                    bc_obj = BonusCategory(
                                        bonus=bonus_obj,
                                        category=wager_cate_obj,
                                    )
                                    bc_obj.save()
                                    logger.info("Create a new BonusCategory for " + str(bonus_obj.name))

                        # add target user group
                        if 'players' in req_data.keys():
                            players = req_data['players']
                            if players.get('target_player'):
                                for key in players.get('target_player'):
                                    ni_group = BonusUserGroup(
                                        bonus=bonus_obj,
                                        groups=UserGroup.objects.get(pk=key)
                                    )
                                    ni_group.save()
                            if players.get('excluded_player'):
                                for key in players.get('excluded_player'):
                                    ne_group = BonusUserGroup(
                                        bonus=bonus_obj,
                                        groups=UserGroup.objects.get(pk=key),
                                        excluded=True
                                    )
                                    ne_group.save()
                            logger.info("Add new groups info for bonus " + str(bonus_obj.name))

                    # if 'categories' in req_data.keys():
                    #     print(req_data['categories'])
                    #     try:
                    #         categories = req_data['categories']
                    #         for cat in categories:
                    #             cat_pk = cat[0]['pk']
                    #             bc_obj = BonusCategory(
                    #                 bonus=bonus_obj,
                    #                 category=Category.objects.get(pk=cat_pk),
                    #             )
                    #             bc_obj.save()
                    #
                    #     except Exception as e:
                    #         logger.error("Error saving new BonusCategory object: ", e)
                    #         return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

                    # add target user group
        except Exception as e:
            logger.error("Error creating new bonus details " + str(e))
            response = JsonResponse({"error": "Error creating new bonus, please try again!"})
            response.status_code = 400
            return response

        # I don't think we should allow all the fields of a bonus to be updated
        # We also assume we cannot update requirements or categories
        if bonus:
            try:
                bonus.name = req_data.get('name'),
                bonus.description = req_data.get('description'),
                bonus.start_time = dateToDatetime(req_data.get('start_time')),
                bonus.end_time = dateToDatetime(req_data.get('end_time')),
                bonus.expiration_days = req_data.get('expiration_days'),
                bonus.countries = req_data.get('countries'),
                bonus.amount = req_data.get('amount'),
                bonus.percentage = req_data.get('percentage'),
                bonus.coupon_code = req_data.get('coupon_code'),
                bonus.affiliate_limit = req_data.get('affiliate_limit'),
                bonus.image_s3 = req_data.get('image_s3'),
                bonus.status = int(req_data.get('status')),
                bonus.issued = req_data.get('issued'),
                bonus.max_daily_times = int(req_data.get('max_daily_times')) or 1,
                bonus.max_total_times = int(req_data.get('max_total_times')) or 1,
                bonus.max_relevant_times = int(req_data.get('max_associated_accounts')) or sys.maxsize,
                bonus.max_users = int(req_data.get('max_user')) or sys.maxsize,
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
            # pagination
            length = int(request.GET.get('length', 20))
            start = int(request.GET.get('start', 0))
            search_value = request.GET.get('search', None)
            order_column = int(request.GET.get('order[0][column]', -1))
            order = request.GET.get('order[0][dir]')
            # filter
            bonus_type = int(request.GET.get('bonus_type', -1))
            ube_status = int(request.GET.get('ube_status', -1))
            min_date = request.GET.get('min_date')
            max_date = request.GET.get('max_date')
            export = request.GET.get('export')
            if export:
                bonus_records_export = [json.loads(request.GET.get('tableHead'))]

            result = {}
            ube_filter = Q()

            total = UserBonusEvent.objects.all().count()

            if min_date and max_date:
                ube_filter &= (Q(delivery_time__gte=dateToDatetime(min_date)) & Q(
                    delivery_time__lte=dateToDatetime(max_date)))

            if bonus_pk:
                ube_filter &= Q(bonus=bonus_pk)

            if user_pk:
                ube_filter &= Q(owner=user_pk)

            if bonus_type != -1:
                ube_filter &= Q(bonus__type=bonus_type)

            if ube_status != -1:
                ube_filter &= Q(status=ube_status)

            #  SEARCH BOX
            if search_value:
                ube_filter &= (Q(owner__username__icontains=search_value) | Q(bonus__name__icontains=search_value) | Q(
                    pk__contains=search_value))

            events = UserBonusEvent.objects.filter(ube_filter).order_by('-delivery_time')

            # START TIME SORTING

            if order_column:
                if order == 'desc':
                    events = events.order_by('-delivery_time')[start:start + length]
                else:
                    events = events.order_by('delivery_time')[start:start + length]
            else:
                events = events[start:start + length]

            count = events.count()

            result['data'] = []
            # put bonus data and user data into events
            # TODO: needs to update ube amount(fixed, percentage, tiered), completion
            for event in events:
                event_data = serializers.serialize('json', {event})
                event_data = json.loads(event_data)

                bonus_data = serializers.serialize('json', {event.bonus})
                bonus_data = json.loads(bonus_data)

                bonus_data[0]['fields'] = bonusValueToKey(bonus_data[0]['fields'])
                event_data[0]['fields'] = ubeValueToKey(event_data[0]['fields'])

                ube_data = {
                    'event': event_data[0],
                    'bonus': bonus_data[0],
                    'username': event.owner.username,
                    'delivered_by_username': event.delivered_by.username
                }
                if export:
                    bonus_records_export.append([
                        event_data[0]['pk'],
                        event_data[0]['fields']['owner'],
                        event.owner.username,
                        bonus_data[0]['fields']['type'],
                        bonus_data[0]['fields']['name'],
                        event_data[0]['fields']['delivery_time'],
                        event_data[0]['fields']['completion_time'],
                        bonus_data[0]['fields']['amount'],
                        event_data[0]['fields']['completion_percentage'],
                        event.delivered_by.username,
                        event_data[0]['fields']['status'],
                    ])
                result['data'].append(ube_data)

            if export:
                return streamingExport(bonus_records_export, 'Bonus Transactions')

            result['recordsTotal'] = total
            result['recordsFiltered'] = count
        except Exception as e:
            logger.error("Error getting UserBonusEvent objects: ", str(e))
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(json.dumps(result), content_type='application/json', status=status.HTTP_200_OK)

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
            event_obj = UserBonusEvent(
                owner=cuser_obj,
                bonus=bonus_obj,
                timestamp=timezone.now(),
                delivered_by=delivered_by_obj,
                status=request.GET.get('status'),
                notes=request.GET.get('notes'),
                amount=request.GET.get('amount'),

            )
            event_obj.save()
        except Exception as e:
            logger.error("Error saving new UserBonusEvent object: ", e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(status=status.HTTP_200_OK)
