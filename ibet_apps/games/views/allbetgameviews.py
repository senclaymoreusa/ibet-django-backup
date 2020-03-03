# Django
from django.views import View
from django.http import HttpResponse
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

# iBet
from users.models import CustomUser
from games.models import GameBet, GameProvider, Category
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys

# Libraries
import json
import logging
import random
import base64
import hashlib
import secrets
import urllib
import requests
import pyDes
import decimal
import hmac
from hashlib import sha1

logger = logging.getLogger('django')

class GameLaunchView(View):
    """
    This endpoint is used to create a launch URL for a user.
    """

    def threeDES(self, query_string):
        """
        Encrypts key-value pairs using 3DES cipher
        """
        # Convert provided key and IV from base64 to bytes. 
        byte_key = base64.b64decode(ALLBET_DES_KEY)
        byte_iv = base64.b64decode(ALLBET_BASE64_IV)
        
        # Encrypt using CBC mode.
        des_obj = pyDes.triple_des(byte_key, pyDes.CBC, byte_iv, pad=None, padmode=pyDes.PAD_PKCS5)
        byte_query_string = query_string.encode()
        encrypted_msg = des_obj.encrypt(byte_query_string)

        # Convert encrypted_msg (bytes) to base64 string.
        data_bytes = base64.b64encode(encrypted_msg)
        data_string = data_bytes.decode()

        return data_string


    def md5(self, data_string):
        """
        Signs encrypted data using MD5 hashing
        """
        string_to_sign = data_string + ALLBET_MD5_KEY
        hashed_result = hashlib.md5(string_to_sign.encode())
        byte_result = hashed_result.digest()

        # Convert byte_result to base64 string.
        sign_bytes = base64.b64encode(byte_result)
        sign_string = sign_bytes.decode()

        return sign_string


    def get(self, request, *args, **kwargs):
        """
        (1) Return launch URL if login is successful (client exists and password is correct)
        (2) If client does not exist, create client and re-launch
        (3) If password is incorrect, reset password and re-launch
        """
        try:
            client_name = request.GET.get("client")

            secure_random_number = secrets.randbits(32) # 32-bit random integer
            query_string = "random=" + str(secure_random_number) + "&client=" + client_name + "&password=" + ALLBET_LAUNCHKEY

            data_string = self.threeDES(query_string)
            sign_string = self.md5(data_string)

            # Create encoded URL parameters.
            req_params = {}
            req_params["propertyId"] = ALLBET_PROP_ID
            req_params["data"] = data_string
            req_params["sign"] = sign_string
            encoded_params = urllib.parse.urlencode(req_params)

            url = AB_URL + "forward_game" + '?' + encoded_params
            response = requests.get(url)

            # Handle all possible scenarios in order to return a game launch URL.
            if response.json()['error_code'] == 'OK':
                logger.info("AllBet game launch attempted with correct username and password combination.")
                return HttpResponse(response.json()['gameLoginUrl'])

            elif response.json()['error_code'] == 'CLIENT_NOT_EXIST':
                logger.error("AllBet game launch attempted with client that does not exist.")
                secure_random_number = secrets.randbits(32) # 32-bit random integer
                query_string = "random=" + str(secure_random_number) + "&agent=" + ALLBET_AGENTNAME + "&client=" + client_name + "&password=" + ALLBET_LAUNCHKEY + "&orHandicapNames=A" + "&vipHandicapNames=VIP_O" + "&orHallRebate=0"

                data_string = self.threeDES(query_string)
                sign_string = self.md5(data_string)

                # Create encoded URL parameters.
                req_params = {}
                req_params["propertyId"] = ALLBET_PROP_ID
                req_params["data"] = data_string
                req_params["sign"] = sign_string
                encoded_params = urllib.parse.urlencode(req_params)

                url = AB_URL + "create_client" + '?' + encoded_params
                response = requests.get(url)

                # Client has been created; re-attempt forward game.
                secure_random_number = secrets.randbits(32) # 32-bit random integer
                query_string = "random=" + str(secure_random_number) + "&client=" + client_name + "&password=" + ALLBET_LAUNCHKEY

                data_string = self.threeDES(query_string)
                sign_string = self.md5(data_string)

                # Create encoded URL parameters.
                req_params = {}
                req_params["propertyId"] = ALLBET_PROP_ID
                req_params["data"] = data_string
                req_params["sign"] = sign_string
                encoded_params = urllib.parse.urlencode(req_params)

                url = AB_URL + "forward_game" + '?' + encoded_params
                response = requests.get(url)
                return HttpResponse(response.json()['gameLoginUrl'])

            elif response.json()['error_code'] == 'CLIENT_PASSWORD_INCORRECT':
                logger.error("AllBet game launch attempted with incorrect password for client.")
                secure_random_number = secrets.randbits(32) # 32-bit random integer
                query_string = "random=" + str(secure_random_number) + "&client=" + client_name + "&newPassword=" + ALLBET_LAUNCHKEY

                data_string = self.threeDES(query_string)
                sign_string = self.md5(data_string)

                # Create encoded URL parameters.
                req_params = {}
                req_params["propertyId"] = ALLBET_PROP_ID
                req_params["data"] = data_string
                req_params["sign"] = sign_string
                encoded_params = urllib.parse.urlencode(req_params)

                url = AB_URL + "setup_client_password" + '?' + encoded_params
                response = requests.get(url)

                # Password has been reset; re-attempt forward game.
                secure_random_number = secrets.randbits(32) # 32-bit random integer
                query_string = "random=" + str(secure_random_number) + "&client=" + client_name + "&password=" + ALLBET_LAUNCHKEY

                data_string = self.threeDES(query_string)
                sign_string = self.md5(data_string)

                # Create encoded URL parameters.
                req_params = {}
                req_params["propertyId"] = ALLBET_PROP_ID
                req_params["data"] = data_string
                req_params["sign"] = sign_string
                encoded_params = urllib.parse.urlencode(req_params)

                url = AB_URL + "forward_game" + '?' + encoded_params
                response = requests.get(url)
                return HttpResponse(response.json()['gameLoginUrl'])

            # Case where provider changes API error_code responses.
            logger.error("AllBet game launch error: forward_game responded with an error_code not specificed in API documentation.")
            return HttpResponse(json.dumps(response.json()), content_type='application/json')

        except Exception as e:
            logger.error("AllBet GameLaunchView Error: " + str(e))
            return HttpResponse("AllBet GameLaunchView Error: " + str(e))


class NoClientBalanceView(View):

    def get(self, request):
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter",
            }
            logger.error("AllBet BalanceView Error: attempted to retrieve balance with missing client parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


class BalanceView(View):
    
    def get(self, request, player_account_name):
        """
        Partner Public Platform API that retrieves the wallet balance of a player. The AllBet property ID and SHA1 key 
        are used along with the request DATE header to generate a signature, which is checked against the signature
        provided in the request AUTHORIZATION header. If the signatures match, return the balance of the player; otherwise,
        return an error code.
        """

        # Case where client does not exist.
        try:
            user_obj = CustomUser.objects.get(username=player_account_name)
        except ObjectDoesNotExist:
            json_to_return = {
                                "error_code": 10003,
                                "message": "Specified user does not exist."
                             }
            logger.error("AllBet BalanceView: User " + str(player_account_name) + " does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        try:
            auth_header = request.META['HTTP_AUTHORIZATION']
            date_header = request.META['HTTP_DATE']

            # Isolate Property ID from request header.
            ab_with_prop_id = str(auth_header).split(":")[0]
            prop_id = ab_with_prop_id[3:]
            
            # Exit and return JSON if property ID is invalid.
            if ALLBET_PROP_ID != prop_id:
                json_to_return = {
                                    "error_code": 10000,
                                    "message": "Invalid authorization property ID"
                                 }
                logger.error("AllBet BalanceView Error: Invalid authorization property ID")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

            # Generate signature.
            string_to_sign = "GET" + "\n" + "" + "\n" + "" + "\n" + date_header + "\n" + "/get_balance/" + player_account_name
            string_to_sign_encoded = string_to_sign.encode()

            hmac_obj = hmac.new(base64.b64decode(ALLBET_SHA1_KEY), string_to_sign_encoded, sha1)
            digest_result = hmac_obj.digest()

            sign_bytes = base64.b64encode(digest_result)
            sign_string = sign_bytes.decode()

            generated_header = "AB" + " " + ALLBET_PROP_ID + ":" + sign_string
            # print(generated_header) # Keeping this print statement for testing purposes.

            if auth_header != generated_header:
                json_to_return = {
                                    "error_code": 10001,
                                    "message": "signature invalid",
                                    "balance": 0 # Provider's instructions
                                 }
                logger.error("AllBet BalanceView Error: Invalid sign while attempting to retrieve balance for user " + str(player_account_name))
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')
            else:
                user_obj = CustomUser.objects.get(username=player_account_name) # Guaranteed to exist at this point in code execution.
                json_to_return = {
                                    "error_code": 0,
                                    "balance": int(user_obj.main_wallet * 100) / 100.0 # Truncate to 2 decimal places.
                                 }
                logger.info("AllBet BalanceView Success: Retrieved balance for user " + str(user_obj.username))
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except Exception as e:
            json_to_return = {
                                "error_code": 50000,
                                "message": "server error: " + str(e),
                                "balance": 0
                             }
            logger.critical("Generic AllBet BalanceView Error: " + str(e))
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


def placeBet(client, transaction_id, amount, bet_details, currency):
    """
    Helper method for the place bet transfer type, which handles both single bets as well
    as batch bets.
    """

    # Idempotence - check if bet transaction ID already used.
    try:
        existing_transactions = GameBet.objects.filter(other_data__transaction_id=transaction_id)

        if existing_transactions.count() >= 1:
            json_to_return = {
                "error_code": 10007,
                "message": "Error: transaction ID already used."
            }
            logger.error("AllBet TransferView: Bet transaction ID already used.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
    except:
        pass

    bet_details_total_amount = 0

    for bet_dictionary in bet_details:
        single_bet_amount = bet_dictionary["amount"]

        if single_bet_amount <= 0:
            json_to_return = {
                "error_code": 40000,
                "message": "Error: Single bet amount cannot be less than or equal to 0."
            }
            logger.warning("AllBet TransferView: Single bet amount cannot be less than or equal to 0.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
        
        bet_details_total_amount += single_bet_amount

    if bet_details_total_amount != amount:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Total bet amount does not add up to the bet amounts in details parameter."
        }
        logger.error("AllBet TransferView: Total bet amount does not add up to the bet amounts in details parameter.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    # Illegal operation: total bet amount is 0 or negative.
    if float(amount) <= 0:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Total bet amount cannot be less than or equal to 0."
        }
        logger.warning("AllBet TransferView: Total bet amount cannot be less than or equal to 0.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    # At this point, we know that the bet request is a valid single or batch bet.
    try:
        user_obj = CustomUser.objects.get(username=client)
        user_balance = int(user_obj.main_wallet * 100) / 100.0 
        bet_amount = float(amount)

        # Bet can go through.
        if user_balance >= bet_amount:
            for bet_entry in bet_details:
                single_bet_id = bet_entry["betNum"]
                single_bet_amount = bet_entry["amount"]

                with transaction.atomic():
                    user_balance = user_obj.main_wallet
                    balance_after_placing = user_balance - decimal.Decimal(single_bet_amount)
                    user_obj.main_wallet = balance_after_placing
                    user_obj.save()

                    ibet_trans_id = user_obj.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                    GameBet.objects.create(
                        provider = GameProvider.objects.get(provider_name=ALLBET_PROVIDER),
                        category = Category.objects.get(name="Live Casino"),
                        #game = None,
                        #game_name = None,
                        user = user_obj,
                        user_name = user_obj.username,
                        amount_wagered = single_bet_amount,
                        amount_won = None,
                        #outcome = None,
                        #odds = None,
                        #bet_type = None,
                        #line = None,
                        transaction_id = ibet_trans_id,
                        currency = user_obj.currency,
                        market = ibetCN,
                        ref_no = single_bet_id,
                        bet_time = timezone.now(),
                        #resolved_time = timezone.now(),
                        other_data = {
                            "transaction_id": transaction_id,
                            "currency": currency
                        }
                    )

            json_to_return = {
                "error_code": 0,
                "balance": int(user_obj.main_wallet * 100) / 100.0
            }
            logger.info("AllBet TransferView Success: Bet(s) placed.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        # User does not have enough money.
        else:
            json_to_return = {
                "error_code": 10101,
                "message": "User does not have enough money to place bet."
            }
            logger.warning("AllBet TransferView: User does not have enough money to place bet.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
    
    except Exception as e:
        if str(e) == "CustomUser matching query does not exist.":
            json_to_return = {
                "error_code": 10003,
                "message": "Specified user does not exist."
            }
            logger.error("AllBet TransferView: Specified user does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        logger.critical("AllBet TransferView: FATAL__ERROR in placeBet function - " + str(e))
        return HttpResponse(str(e))


def settleBet(client, transaction_id, amount, settle_details, currency):
    """
    Helper method for the settle bet transfer type. 'amount' parameter will be positive for wins and negative for losses.
    This method supports batch settling of bets.
    """

    # Batch settlement is not allowed.
    if len(settle_details) > 1:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Batch settlement is not allowed."
        }
        logger.error("AllBet Transfer: batch settlement is not allowed.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    # Idempotence - check if transaction_id already used.
    try:
        existing_transactions = GameBet.objects.filter(other_data__transaction_id=transaction_id)

        if existing_transactions.count() >= 1:
            json_to_return = {
                "error_code": 10007,
                "message": "Error: transaction ID already used."
            }
            logger.error("AllBet TransferView: Cannot settle since Transaction ID is already used.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
    except:
        pass

    settle_details_total_amount = 0

    for settle_dictionary in settle_details:
        settle_details_total_amount += settle_dictionary["amount"]
        single_settle_id = settle_dictionary["betNum"]

        try:
            existing_transaction = GameBet.objects.get(ref_no=single_settle_id)

            # 3-16: Settling with a different client account should not be allowed
            if existing_transaction.user_name != client:
                json_to_return = {
                    "error_code": 10007,
                    "message": "invalid status: transaction had already been cancelled/settled"
                }
                logger.error("AllBet TransferView Error: invalid request parameter")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

            # 3-15: Settling with different currencies should not be allowed
            if existing_transaction.other_data["currency"] != currency:
                json_to_return = {
                    "error_code": 40000,
                    "message": "invalid request parameter"
                }
                logger.error("AllBet TransferView Error: invalid request parameter")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except ObjectDoesNotExist:
            json_to_return = {
                "error_code": 10006,
                "message": "Error: Attempted to settle a bet that does not exist."
            }
            logger.error("AllBet TransferView: Attempted to settle a bet that does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    if settle_details_total_amount != amount:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Total settle amount does not add up to the settle amount in details parameter."
        }
        logger.error("AllBet TransferView: Total settle amount does not add up to the settle amount in details parameter.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    try:
        user_obj = CustomUser.objects.get(username=client)
        user_balance = int(user_obj.main_wallet * 100) / 100.0

        # Loop through settle_details and settle bets individually.
        for settle_entry in settle_details:
            single_settle_id = settle_entry["betNum"]
            single_settle_amount = settle_entry["amount"]

            with transaction.atomic():
                existing_transaction = GameBet.objects.get(ref_no=single_settle_id)
                prev_bet_amount = existing_transaction.amount_wagered

                user_balance = user_obj.main_wallet
                balance_after_settling = user_balance + decimal.Decimal(single_settle_amount) + prev_bet_amount
                user_obj.main_wallet = balance_after_settling
                user_obj.save()

                ibet_trans_id = user_obj.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                settle_outcome = None
                if single_settle_amount > 0:
                    settle_outcome = 0 # Win
                elif single_settle_amount < 0:
                    settle_outcome = 1 # Lose
                else:
                    settle_outcome = 2 # Tie

                GameBet.objects.create(
                    provider = GameProvider.objects.get(provider_name=ALLBET_PROVIDER),
                    category = Category.objects.get(name="Live Casino"),
                    #game = None,
                    #game_name = None,
                    user = user_obj,
                    user_name = user_obj.username,
                    amount_wagered = 0.00,
                    amount_won = single_settle_amount,
                    outcome = settle_outcome,
                    #odds = None,
                    #bet_type = None,
                    #line = None,
                    transaction_id = ibet_trans_id,
                    currency = user_obj.currency,
                    market = ibetCN,
                    ref_no = single_settle_id,
                    #bet_time = timezone.now(),
                    resolved_time = timezone.now(),
                    other_data = {
                        "transaction_id": transaction_id,
                        "currency": currency
                    }
                )

        json_to_return = {
            "error_code": 0,
            "balance": int(user_obj.main_wallet * 100) / 100.0
        }
        logger.info("AllBet TransferView Success: Bet(s) settled.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    except Exception as e:
        if str(e) == "CustomUser matching query does not exist.":
            json_to_return = {
                "error_code": 10003,
                "message": "Specified user does not exist."
            }
            logger.error("AllBet TransferView: Specified user does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        logger.critical("AllBet TransferView: FATAL__ERROR in settleBet function - " + str(e))
        return HttpResponse(str(e))


def cancelBet(client, transaction_id, amount, cancel_details, currency):
    try:

        try:
            existing_transactions = GameBet.objects.filter(other_data__transaction_id=transaction_id)

            if existing_transactions.count() >= 1:
                json_to_return = {
                    "error_code": 10007,
                    "message": "Error: transaction ID already used."
                }
                logger.error("AllBet TransferView: Cannot cancel since Transaction ID is already used.")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')
        except:
            pass


        try:
            user_obj = CustomUser.objects.get(username=client)
        except ObjectDoesNotExist:
            json_to_return = {
                "error_code": 10003,
                "message": "Specified user does not exist."
            }
            logger.error("AllBet TransferView: Specified user does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        if amount <= 0:
            json_to_return = {
                "error_code": 40000,
                "message": "Cannot cancel negative or zero total bet amount"
            }
            logger.warning("AllBet TransferView: Cannot cancel negative or zero total bet amount")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        cancel_details_total_amount = 0

        for cancel_dictionary in cancel_details:
            cancel_details_total_amount += cancel_dictionary["amount"]
            single_cancel_id = cancel_dictionary["betNum"]

            if cancel_dictionary["amount"] <= 0:
                json_to_return = {
                    "error_code": 40000,
                    "message": "Error: Negative or zero bet amount in details."
                }
                logger.error("AllBet TransferView: Negative or zero bet amount in details.")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

            try:
                existing_bet = GameBet.objects.get(ref_no=single_cancel_id)

                if existing_bet.amount_wagered != cancel_dictionary["amount"]:
                    json_to_return = {
                        "error_code": 40000,
                        "message": "Error: Bet amount and cancel amount do not match."
                    }
                    logger.error("AllBet TransferView: Bet amount and cancel amount do not match.")
                    return HttpResponse(json.dumps(json_to_return), content_type='application/json')

                # 2-17: Cancelling with a different client account should not be allowed
                if existing_bet.user_name != client:
                    json_to_return = {
                        "error_code": 10007,
                        "message": "invalid status: transaction had already been cancelled/settled"
                    }
                    logger.error("AllBet TransferView Error: invalid request parameter")
                    return HttpResponse(json.dumps(json_to_return), content_type='application/json')

                # 2-16: Cancelling with different currencies should not be allowed
                if existing_bet.other_data["currency"] != currency:
                    json_to_return = {
                        "error_code": 40000,
                        "message": "invalid request parameter"
                    }
                    logger.error("AllBet TransferView Error: invalid request parameter")
                    return HttpResponse(json.dumps(json_to_return), content_type='application/json')

            except ObjectDoesNotExist:
                json_to_return = {
                    "error_code": 10006,
                    "message": "Error: Attempted to cancel a bet that does not exist."
                }
                logger.error("AllBet TransferView: Attempted to cancel a bet that does not exist.")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        if cancel_details_total_amount != amount:
            json_to_return = {
                "error_code": 40000,
                "message": "Error: Total cancel amount does not add up to the cancel amount in details parameter."
            }
            logger.error("AllBet TransferView: Total cancel amount does not add up to the cancel amount in details parameter.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        user_balance = int(user_obj.main_wallet * 100) / 100.0

        # Cancel bets individually.
        for cancel_entry in cancel_details:
            single_cancel_id = cancel_entry["betNum"]
            single_cancel_amount = cancel_entry["amount"]

            with transaction.atomic():
                user_balance = user_obj.main_wallet
                balance_after_cancelling = user_balance + decimal.Decimal(single_cancel_amount)
                user_obj.main_wallet = balance_after_cancelling
                user_obj.save()

                ibet_trans_id = user_obj.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                GameBet.objects.create(
                    provider = GameProvider.objects.get(provider_name=ALLBET_PROVIDER),
                    category = Category.objects.get(name="Live Casino"),
                    #game = None,
                    #game_name = None,
                    user = user_obj,
                    user_name = user_obj.username,
                    amount_wagered = 0.00,
                    amount_won = single_cancel_amount,
                    outcome = 3, # Cancel/ Void
                    #odds = None,
                    #bet_type = None,
                    #line = None,
                    transaction_id = ibet_trans_id,
                    currency = user_obj.currency,
                    market = ibetCN,
                    ref_no = single_cancel_id,
                    #bet_time = timezone.now(),
                    resolved_time = timezone.now(),
                    other_data = {
                        "transaction_id": transaction_id,
                        "currency": currency
                    }
                )

        json_to_return = {
            "error_code": 0,
            "balance": int(user_obj.main_wallet * 100) / 100.0
        }
        logger.info("AllBet TransferView Success: Bet(s) cancelled.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    except Exception as e:
        # Generic
        logger.critical("AllBet TransferView: FATAL__ERROR in cancelBet function - " + str(e))
        return HttpResponse(str(e))


def resettleBet(client, transaction_id, amount, resettle_details, currency):

    try:
        existing_settle = GameBet.objects.filter(ref_no=resettle_details[0]["betNum"])

        # 4-21: Re-settle with different currencies
        if existing_settle.other_data["currency"] != currency:
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        # 4-22: Re-settle with another client account
        if existing_settle.user_name != client:
            json_to_return = {
                "error_code": 10007,
                "message": "invalid status: transaction had already been cancelled/settled"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    except ObjectDoesNotExist:
        json_to_return = {
            "error_code": 10006,
            "message": "Error: Attempted to re-settle non-existing bet."
        }
        logger.error("AllBet TransferView: Attempted to re-settle non-existing bet.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')


    try:
        existing_transactions = GameBet.objects.filter(other_data__transaction_id=transaction_id)

        if existing_transactions.count() >= 1:
            json_to_return = {
                "error_code": 10007,
                "message": "Error: transaction ID already used."
            }
            logger.error("AllBet TransferView: Cannot re-settle since Transaction ID is already used.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
    except:
        pass


    try:
        user_obj = CustomUser.objects.get(username=client)
    except ObjectDoesNotExist:
        json_to_return = {
            "error_code": 10003,
            "message": "Specified user does not exist."
        }
        logger.error("AllBet TransferView: Specified user does not exist.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')


    if len(resettle_details) > 1:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Batch re-settling is not allowed."
        }
        logger.warning("AllBet TransferView: Batch re-settling is not allowed.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')


    try:
        resettle_id = resettle_details[0]["betNum"]

        # Case 4-17
        resettle_amount = resettle_details[0]["amount"]
        if resettle_amount != amount:
            json_to_return = {
                "error_code": 40000,
                "message": "Error: total win/loss not equal to win/loss in details parameter"
            }
            logger.warning("AllBet TransferView: total win/loss not equal to win/loss in details parameter.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        try:
            most_recent_settle = GameBet.objects.filter(ref_no=resettle_id, outcome__in=[0, 1, 2, 3]).latest('resolved_time')
        except ObjectDoesNotExist:
            # In this case, a bet is directly being re-settled without a prior settle.
            return settleBet(client, transaction_id, amount, resettle_details)

        # Cancel existing settle and re-settle according to new details.
        with transaction.atomic():
            user_balance = user_obj.main_wallet
            balance_after_cancelling = user_balance - most_recent_settle.amount_won
            balance_after_resettling = balance_after_cancelling + decimal.Decimal(resettle_details[0]["amount"])
            user_obj.main_wallet = balance_after_resettling
            user_obj.save()

            ibet_trans_id = user_obj.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

            GameBet.objects.create(
                provider = GameProvider.objects.get(provider_name=ALLBET_PROVIDER),
                category = Category.objects.get(name="Live Casino"),
                #game = None,
                #game_name = None,
                user = user_obj,
                user_name = user_obj.username,
                amount_wagered = 0.00,
                amount_won = resettle_details[0]["amount"],
                outcome = 3, # rollback
                #odds = None,
                #bet_type = None,
                #line = None,
                transaction_id = ibet_trans_id,
                currency = user_obj.currency,
                market = ibetCN,
                ref_no = resettle_id,
                #bet_time = timezone.now(),
                resolved_time = timezone.now(),
                other_data = {
                    "transaction_id": transaction_id,
                    "currency": currency
                }
            )

            json_to_return = {
                "error_code": 0,
                "balance": int(user_obj.main_wallet * 100) / 100.0
            }
            logger.info("AllBet TransferView Success: Bet re-settled.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    except Exception as e:
        json_to_return = {
            "error_code": 50000,
            "message": "AllBet transfer error: " + str(e)
        }
        logger.critical("AllBet TransferView: FATAL__ERROR in resettleBet function - " + str(e))
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')


class TransferView(View):

    def post(self, request, *args, **kwargs):
        """
        Partner Public Platform API that handles different wallet transfer types such as bet, cancel, settle,
        and re-settle. JSON is the data format that this endpoint receives and responds with.
        """

        try:
            transfer_type = json.loads(request.body)["transferType"]
        except:
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        try:
            client = json.loads(request.body)["client"]

            if client == "":
                json_to_return = {
                    "error_code": 40000,
                    "message": "invalid request parameter"
                }
                logger.error("AllBet TransferView Error: invalid request parameter")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except:
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        try:
            tran_id = json.loads(request.body)["tranId"]

            if tran_id == "":
                json_to_return = {
                    "error_code": 40000,
                    "message": "invalid request parameter"
                }
                logger.error("AllBet TransferView Error: invalid request parameter")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except:
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        try:
            amount = json.loads(request.body)["amount"]

            if amount == "":
                json_to_return = {
                    "error_code": 40000,
                    "message": "invalid request parameter"
                }
                logger.error("AllBet TransferView Error: invalid request parameter")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except:
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        try:
            currency = json.loads(request.body)["currency"]

            if currency == "":
                json_to_return = {
                    "error_code": 40000,
                    "message": "invalid request parameter"
                }
                logger.error("AllBet TransferView Error: invalid request parameter")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except:
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        # Check details, betNum, & amount
        try:
            details = json.loads(request.body)["details"]

            # Loop through details and check amount & betNum for each entry
            for details_entry in details:
                try:
                    betNum = details_entry["betNum"]
                    amount = details_entry["amount"]

                    # empty betNum or amount
                    if (betNum == "") or (amount == ""):
                        json_to_return = {
                            "error_code": 40000,
                            "message": "invalid request parameter"
                        }
                        logger.error("AllBet TransferView Error: invalid request parameter")
                        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

                    if (betNum == "invalid") or (amount == "invalid"):
                        json_to_return = {
                            "error_code": 40000,
                            "message": "invalid request parameter"
                        }
                        logger.error("AllBet TransferView Error: invalid request parameter")
                        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

                except:
                    # missing betNum or amount
                    json_to_return = {
                        "error_code": 40000,
                        "message": "invalid request parameter"
                    }
                    logger.error("AllBet TransferView Error: invalid request parameter")
                    return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        except:
            # missing details parameter
            json_to_return = {
                "error_code": 40000,
                "message": "invalid request parameter"
            }
            logger.error("AllBet TransferView Error: invalid request parameter")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        try:
            json_data = json.loads(request.body)

            client = json_data["client"]
            transaction_id = json_data["tranId"]
            amount = json_data["amount"]
            currency = json_data["currency"]
            transfer_type = json_data["transferType"]
            bet_details = json_data["details"]


            if (transaction_id == "invalid") or (amount == "invalid") or (currency == "invalid"):
                json_to_return = {
                    "error_code": 40000,
                    "message": "invalid request parameter"
                }
                logger.error("AllBet TransferView Error: invalid request parameter")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')


            auth_header = request.META['HTTP_AUTHORIZATION']
            date_header = request.META['HTTP_DATE']
            content_md5_header = request.META['HTTP_CONTENT_MD5']

            # Exit and return JSON if property ID is invalid.
            ab_with_prop_id = str(auth_header).split(":")[0]
            prop_id = ab_with_prop_id[3:]

            if ALLBET_PROP_ID != prop_id:
                json_to_return = {
                                    "error_code": 10000,
                                    "message": "Invalid authorization property ID"
                                 }
                logger.error("AllBet TransferView Error: Invalid authorization property ID")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')

            # Construct string for signing.
            string_to_sign = "POST" + "\n" + content_md5_header + "\n" + "application/json; charset=UTF-8" + "\n" + date_header + "\n" + "/transfer"
            string_to_sign_encoded = string_to_sign.encode()

            # Generate signature
            hmac_obj = hmac.new(base64.b64decode(ALLBET_SHA1_KEY), string_to_sign_encoded, sha1)
            digest_result = hmac_obj.digest()
            sign_bytes = base64.b64encode(digest_result)
            sign_string = sign_bytes.decode()

            generated_auth_header = "AB" + " " + ALLBET_PROP_ID + ":" + sign_string
            # print("generated_auth_header: " + generated_auth_header) # Keeping this for testing purposes.


            if auth_header != generated_auth_header:
                json_to_return = {
                                    "error_code": 10001,
                                    "message": "signature invalid",
                                    "balance": 0
                                 }
                logger.error("AllBet TransferView Error: Invalid sign while attempting to transfer")
                return HttpResponse(json.dumps(json_to_return), content_type='application/json')


            # Default JSON Response fields
            res_error_code = 50000
            res_message = "server error"
            res_balance = 0

            # Place bet
            if transfer_type == 10:
                return placeBet(client, transaction_id, amount, bet_details, currency)

            # Settle bet
            elif transfer_type == 20:
                return settleBet(client, transaction_id, amount, bet_details, currency)

            # Cancel bet
            elif transfer_type == 11:
                return cancelBet(client, transaction_id, amount, bet_details, currency)

            # Re-settle bet
            elif transfer_type == 21:
                return resettleBet(client, transaction_id, amount, bet_details, currency)

            else:
                res_error_code = 40000
                res_message = "AllBet TransferView Error: Invalid transfer type"

            # If we have not yet returned successfully from a helper function, we return with an error.
            json_to_return = {
                                "error_code": res_error_code,
                                "message": res_message,
                                "balance": res_balance
                             }
            return JsonResponse(json_to_return)

        except Exception as e:
            logger.critical("Generic AllBet TransferView Error: " + str(e))
            json_to_return = {
                                "error_code": 50000,
                                "message": "server error: " + str(e),
                                "balance": 0
                             }
            return JsonResponse(json_to_return)
