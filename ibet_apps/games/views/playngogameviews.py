# Django
from django.views import View
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError
from rest_framework import status
from django.db import transaction
from django.utils import timezone

# iBet
from users.models import CustomUser
from games.models import GameBet, GameProvider, Category, PNGTicket
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys
from users.views.helper import checkUserBlock

# Libraries
import xmltodict
import logging
import decimal
import uuid
import random


logger = logging.getLogger('django')

def setup_models():
    PROVIDER = None
    CATEGORY = None 

    try:
        PROVIDER = GameProvider.objects.get(provider_name=PLAYNGO_PROVIDER)
    except ObjectDoesNotExist:
        logger.error("missing playngo provider.")

    try:
        CATEGORY = Category.objects.get(name="Games")
    except ObjectDoesNotExist:
        logger.error("missing category.")
    
    return (PROVIDER, CATEGORY)

class GetPNGTicket(View):
    """
    Test class to simulate a game launch
    """
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.GET.get("userid")
            png_ticket = uuid.uuid4()
            user_obj = CustomUser.objects.get(pk=user_id)

            # Case where user's existing PNGTicket needs to be updated
            try:
                existing_ticket = PNGTicket.objects.get(user_obj=user_obj)
                existing_ticket.png_ticket = png_ticket
                existing_ticket.save()

            # Case where user has never played PNG games before
            except:
                PNGTicket.objects.create(png_ticket=png_ticket, user_obj=user_obj)
            
            json_to_return = { "ticket" : str(png_ticket) }
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except Exception as e:
            logger.critical("PLAY'nGO Game Launch Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


def png_authenticate(data):
    try:
        req_dict = xmltodict.parse(data)

        session_token = req_dict['authenticate']['username']
        product_id = req_dict['authenticate']['productId']
        client_ip = req_dict['authenticate']['clientIP']
        context_id = req_dict['authenticate']['contextId']
        access_token = req_dict['authenticate']['accessToken']
        language = req_dict['authenticate']['language']
        game_id = req_dict['authenticate']['gameId']
        channel = req_dict['authenticate']['channel']

        try:
            existing_ticket = PNGTicket.objects.get(png_ticket=session_token)
            user_obj = existing_ticket.user_obj

            user_registration_time = str(user_obj.time_of_registration).split(" ")[0]

            external_id = user_obj.username
            status_code = PNG_STATUS_OK 
            status_message = "ok"
            user_currency = CURRENCY_CHOICES[user_obj.currency][1]
            country = user_obj.country
            birthdate = user_obj.date_of_birth
            registration = user_registration_time
            res_language = user_obj.language
            affiliate_id = "" # Placeholder
            real = int(user_obj.main_wallet * 100) / 100.0
            external_game_session_id = "" # Placeholder
            
            if checkUserBlock(user_obj):
                status_code = PNG_STATUS_ACCOUNTDISABLED
                status_message = "Account Disabled"

            # Compose response dictionary and convert to response XML
            res_dict = {
                "authenticate": {
                    "externalId": {
                        "#text": str(external_id)
                    },
                    "statusCode": {
                        "#text": str(status_code)
                    },
                    "statusMessage": {
                        "#text": status_message
                    },
                    "userCurrency": {
                        "#text": str(user_currency)
                    },
                    "country": {
                        "#text": str(country)
                    },
                    "birthdate": {
                        "#text": str(birthdate)
                    },
                    "registration": {
                        "#text": str(registration)
                    },
                    "language": {
                        "#text": str(res_language)
                    },
                    "affiliateId": {
                        "#text": affiliate_id
                    },
                    "real": {
                        "#text": str(real)
                    },
                    "externalGameSessionId": {
                        "#text": external_game_session_id
                    },
                }
            }

            res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
            return HttpResponse(res_msg, content_type='text/xml') # Successful response

        except Exception as e:
            logger.critical("PLAY'nGO Authentication Error: " + str(e))

            # Invalid session token
            res_dict = {
                "authenticate": {
                    "statusCode": {
                        "#text": str(PNG_STATUS_WRONGUSERNAMEPASSWORD)
                    },
                    "statusMessage": {
                        "#text": "Wrong Username or Password"
                    },
                }
            }

            res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
            return HttpResponse(res_msg, content_type='text/xml')

    except:
        # Malformed xml, missing tags, or error parsing data
        raise ParseError


def png_balance(data):        
    try:
        req_dict = xmltodict.parse(data)

        username = req_dict['balance']['externalId']
        product_id = req_dict['balance']['productId']
        currency = req_dict['balance']['currency']
        game_id = req_dict['balance']['gameId']
        access_token = req_dict['balance']['accessToken']

        if PNG_ACCESS_TOKEN != access_token:
            res_dict = {
                "balance": {
                    "real": {
                        "#text": str(0.00)
                    },
                    "currency": {
                        "#text": "N/A"
                    },
                    "statusCode": {
                        "#text": str(PNG_STATUS_WRONGUSERNAMEPASSWORD)
                    },
                }
            }

            res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
            return HttpResponse(res_msg, content_type='text/xml')

        # Retrieve balance of specified user and set status code based on user account status.
        user_obj = CustomUser.objects.get(username=username)
        user_balance = int(user_obj.main_wallet * 100) / 100.0
        user_currency = CURRENCY_CHOICES[user_obj.currency][1]
        status_code = PNG_STATUS_OK # Default case is 0 (request successful).

        if checkUserBlock(user_obj):
            status_code = PNG_STATUS_ACCOUNTDISABLED

        # Compose response dictionary and convert to response XML.
        res_dict = {
            "balance": {
                "real": {
                    "#text": str(user_balance)
                },
                "currency": {
                    "#text": str(user_currency)
                },
                "statusCode": {
                    "#text": str(status_code)
                },
            }
        }

        res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
        return HttpResponse(res_msg, content_type='text/xml')

    except Exception as e:
        logger.critical("PLAY'nGO Balance Error: " + str(e))
        return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


def png_reserve(data):
    PROVIDER, CATEGORY = setup_models()

    try:
        req_dict = xmltodict.parse(data)

        username = req_dict['reserve']['externalId']
        product_id = req_dict['reserve']['productId']
        transaction_id = req_dict['reserve']['transactionId']
        bet_amount_str = req_dict['reserve']['real']
        req_currency = req_dict['reserve']['currency']
        game_id = req_dict['reserve']['gameId']
        game_session_id = req_dict['reserve']['gameSessionId']
        access_token = req_dict['reserve']['accessToken']
        round_id = req_dict['reserve']['roundId']
        channel = req_dict['reserve']['channel']
        free_game_external_id = req_dict['reserve']['freegameExternalId']
        actual_value = req_dict['reserve']['actualValue']
        
        user_obj = CustomUser.objects.get(username=username)
        user_balance = user_obj.main_wallet
        bet_amount_decimal = decimal.Decimal(bet_amount_str)
        user_currency_text = CURRENCY_CHOICES[user_obj.currency][1]

        status_code = PNG_STATUS_OK
        bet_already_placed = False

        if checkUserBlock(user_obj):
            logger.error("PLAY'nGO Reserve Error: Blocked users are not allowed to place bets.")

            res_dict = {
                "reserve": {
                    "statusCode": {
                        "#text": str(PNG_STATUS_ACCOUNTDISABLED)
                    },
                    "statusMessage": {
                        "#text": "Account Disabled"
                    },
                }
            }

            res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
            return HttpResponse(res_msg, content_type='text/xml')

        # Idempotence - check if bet with transaction_id was already successfully placed.
        try:
            existing_bet = GameBet.objects.get(ref_no=transaction_id, provider=PROVIDER)
            logger.error("PLAY'nGO: Bet with transaction_id already exists.")
            bet_already_placed = True
        except ObjectDoesNotExist:
            logger.info("PLAY'nGO: Bet with transaction_id does not exist yet.")
            pass

        if bet_already_placed:
            # Skip over all the other possible bet outcomes (elif/else clauses).
            pass

        # Bet can go through. 
        elif user_balance >= bet_amount_decimal:
            with transaction.atomic():
                balance_after_bet = user_balance - bet_amount_decimal
                user_obj.main_wallet = balance_after_bet
                user_obj.save()

                ibet_trans_id = user_obj.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                # Create a GameBet entry upon successful placement of a bet.
                GameBet.objects.create(
                    provider = PROVIDER,
                    category = CATEGORY,
                    #game = None,
                    #game_name = None,
                    user = user_obj,
                    user_name = user_obj.username,
                    amount_wagered = bet_amount_decimal,
                    amount_won = 0.00,
                    #outcome = None,
                    #odds = None,
                    #bet_type = None,
                    #line = None,
                    transaction_id = ibet_trans_id,
                    currency = user_obj.currency,
                    market = ibetVN, # Need to clarify with provider
                    ref_no = transaction_id,
                    #bet_time = None,
                    #resolved_time = None,
                    #other_data = {}
                )

                logger.info("PLAY'nGO Reserve Success: Bet placed for user " + user_obj.username)
        
        # Bet amount is bigger than user balance.
        else:
            status_code = PNG_STATUS_NOTENOUGHMONEY
            logger.error("PLAY'nGO Reserve Error: Not enough money to place bet.")

        # Compose response dictionary and convert to response XML.
        res_dict = {
            "reserve": {
                "real": {
                    # Cannot use balance_after_bet in case bet did not go through
                    "#text": str(int(user_obj.main_wallet * 100) / 100.0)
                },
                "currency": {
                    "#text": str(user_currency_text)
                },
                "statusCode": {
                    "#text": str(status_code)
                },
            }
        }

        res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
        return HttpResponse(res_msg, content_type='text/xml')

    except Exception as e:
        logger.critical("PLAY'nGO Reserve Error: " + str(e))
        return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


def png_cancel_reserve(data):
    PROVIDER, CATEGORY = setup_models()

    try:
        req_dict = xmltodict.parse(data)

        username = req_dict['cancelReserve']['externalId']
        product_id = req_dict['cancelReserve']['productId']
        transaction_id = req_dict['cancelReserve']['transactionId']
        real = req_dict['cancelReserve']['real']
        currency = req_dict['cancelReserve']['currency']
        game_session_id = req_dict['cancelReserve']['gameSessionId']
        access_token = req_dict['cancelReserve']['accessToken']
        round_id = req_dict['cancelReserve']['roundId']
        game_id = req_dict['cancelReserve']['gameId']
        channel = req_dict['cancelReserve']['channel']
        free_game_external_id = req_dict['cancelReserve']['freegameExternalId']
        actual_value = req_dict['cancelReserve']['actualValue']

        status_code = PNG_STATUS_OK
        ext_trans_id = None
        
        user_obj = CustomUser.objects.get(username=username)

        if checkUserBlock(user_obj):
            # Even if the user is blocked, the refund should still go through. No further action is 
            # necessary for this case. This is to explicitly inform the reader that this case is
            # already handled.
            pass

        # Attempt to look up previous bet and cancel.
        try:
            with transaction.atomic():
                existing_bet = GameBet.objects.get(ref_no=transaction_id, provider=PROVIDER) # Provider will not send multiple CancelReserve requests with same id.
                
                user_balance = user_obj.main_wallet
                amount_to_refund = existing_bet.amount_wagered

                balance_after_refund = user_balance + amount_to_refund
                user_obj.main_wallet = balance_after_refund
                user_obj.save()

                ibet_trans_id = user_obj.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                GameBet.objects.create(
                    provider = PROVIDER,
                    category = CATEGORY,
                    #game = None,
                    #game_name = None,
                    user = user_obj,
                    user_name = user_obj.username,
                    amount_wagered = 0.00,
                    amount_won = amount_to_refund,
                    outcome = 3,
                    #odds = None,
                    #bet_type = None,
                    #line = None,
                    transaction_id = ibet_trans_id,
                    currency = user_obj.currency,
                    market = ibetVN, # Need to clarify with provider
                    ref_no = transaction_id,
                    #bet_time = None,
                    resolved_time = timezone.now(),
                    #other_data = {}
                )
                
                logger.info("PLAY'nGO Cancel Reserve Success: Bet successfully refunded.")

        # Specified bet does not exist.
        except ObjectDoesNotExist:
            ext_trans_id = ""
            logger.error("PLAY'nGO Cancel Reserve Error: Specified bet does not exist.")

        # Compose response dictionary and convert to response XML.
        res_dict = {
            "cancelReserve": {
                "transactionId": {
                    "#text": str(transaction_id)
                },
                "externalTransactionId": {
                    "#text": str(ext_trans_id)
                },
                "statusCode": {
                    "#text": str(status_code)
                },
            }
        }

        res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
        return HttpResponse(res_msg, content_type='text/xml')

    except Exception as e:
        logger.critical("PLAY'nGO Cancel Reserve Error: " + str(e))
        return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


def png_release(data):
    PROVIDER, CATEGORY = setup_models()

    try:
        req_dict = xmltodict.parse(data)

        username = req_dict['release']['externalId']
        product_id = req_dict['release']['productId']
        transaction_id = req_dict['release']['transactionId']
        win_amount_str = req_dict['release']['real']
        currency = req_dict['release']['currency']
        game_session_id = req_dict['release']['gameSessionId']
        state = req_dict['release']['state']
        req_type = req_dict['release']['type']
        game_id = req_dict['release']['gameId']
        access_token = req_dict['release']['accessToken']
        round_id = req_dict['release']['roundId']
        jackpot_gain = req_dict['release']['jackpotGain']
        jackpot_loss = req_dict['release']['jackpotLoss']
        jackpot_gain_seed = req_dict['release']['jackpotGainSeed']
        jackpot_gain_id = req_dict['release']['jackpotGainId']
        channel = req_dict['release']['channel']
        free_game_external_id = req_dict['release']['freegameExternalId']
        # free_game_total_gain = req_dict['release']['freegameTotalGain']

        user_obj = CustomUser.objects.get(username=username)
        user_balance = user_obj.main_wallet
        win_amount_decimal = decimal.Decimal(win_amount_str)
        user_currency_text = CURRENCY_CHOICES[user_obj.currency][1]

        status_code = PNG_STATUS_OK
        release_already_resolved = False

        # Idempotence - check if release with transaction_id was already successfully resolved.
        try:
            existing_release = GameBet.objects.get(ref_no=transaction_id, provider=PROVIDER)
            logger.error("PLAY'nGO Release Error: Release with transaction_id already exists.")
            release_already_resolved = True
        except ObjectDoesNotExist:
            pass

        # Release not resolved yet; issue the refund.
        if not release_already_resolved:
            with transaction.atomic():
                balance_after_win = user_balance + win_amount_decimal
                user_obj.main_wallet = balance_after_win
                user_obj.save()

                ibet_trans_id = user_obj.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                GameBet.objects.create(
                    provider = PROVIDER,
                    category = CATEGORY,
                    #game = None,
                    #game_name = None,
                    user = user_obj,
                    user_name = user_obj.username,    
                    amount_wagered = 0.00,
                    amount_won = win_amount_decimal,
                    outcome = 0,
                    #odds = None,
                    #bet_type = None,
                    #line = None,
                    transaction_id = ibet_trans_id,
                    currency = user_obj.currency,
                    market = ibetVN, # Need to clarify with provider
                    ref_no = transaction_id,
                    #bet_time = None,
                    resolved_time = timezone.now(),
                    #other_data = {}
                )

                logger.info("PLAY'nGO Release Success: Winnings sent to user " + str(user_obj.username))

        else:
            logger.error("PLAY'nGO Release Error: Transaction already resolved.")
            pass

        res_dict = {
            "release": {
                "real": {
                    "#text": str(int(user_obj.main_wallet * 100) / 100.0)
                },
                "currency": {
                    "#text": str(user_currency_text)
                },
                "statusCode": {
                    "#text": str(status_code)
                },
            }
        }

        res_msg = xmltodict.unparse(res_dict, pretty=True, full_document=False)
        return HttpResponse(res_msg, content_type='text/xml')

    except Exception as e:
        logger.critical("PLAY'nGO Release Error: " + str(e))
        return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


class RootView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = request.body
            req_dict = xmltodict.parse(data)
            root_elem_name = list(req_dict.keys())[0]

            if root_elem_name == "authenticate":
                return png_authenticate(data)

            elif root_elem_name == "reserve":
                return png_reserve(data)

            elif root_elem_name == "release":
                return png_release(data)

            elif root_elem_name == "balance":
                return png_balance(data)

            elif root_elem_name == "cancelReserve":
                return png_cancel_reserve(data)

            else:
                # Provider says this case should never occur.
                logger.error("Playngo: Invalid request received.")
                return HttpResponse("Playngo: Invalid request received.", status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.critical("General error in Playngo: " + str(e))
            return HttpResponse(str(e))
