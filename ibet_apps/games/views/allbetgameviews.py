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

class EncryptionView(View):
    """
    This test class is used for DES encryption and MD5 signing, which is necessary for all requests 
    to test the AllBet API as part of the 'Test Plan on API Integration Test' to be submitted to 
    AllBet's QA Department for verification.

    Overview
        (1) Build query string
        (2) Encrypt query string using 3DES (data paraneter)
        (3) Hash the encrypted query string using MD5 (sign parameter)
        (4) Set propertyId, data, and sign parameters of request
        (5) Send request and verify JSON response
    """

    third_party_keys = getThirdPartyKeys("ibet-admin-eudev", "config/gamesKeys.json")
    AB_PROPERTY_ID = third_party_keys["ALLBET"]["PROPERTYID"]
    AB_DES_KEY = third_party_keys["ALLBET"]["DESKEY"]
    AB_MD5_KEY = third_party_keys["ALLBET"]["MD5KEY"]
    AB_BASE64_IV = third_party_keys["ALLBET"]["BASE64IV"]

    # These values may change based on the test so they should not be put under utils/constants.
    agent_name = "ftrwaa"
    endpoint = AB_URL + "query_agent_handicaps"


    def threeDES(self, query_string):
        """
        Encrypts key-value pairs using 3DES cipher
        """
        # Convert provided key and IV from base64 to bytes. 
        byte_key = base64.b64decode(self.AB_DES_KEY)
        byte_iv = base64.b64decode(self.AB_BASE64_IV)
        
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
        string_to_sign = data_string + self.AB_MD5_KEY
        hashed_result = hashlib.md5(string_to_sign.encode())
        byte_result = hashed_result.digest()

        # Convert byte_result to base64 string.
        sign_bytes = base64.b64encode(byte_result)
        sign_string = sign_bytes.decode()

        return sign_string


    def get(self, request, *args, **kwargs):
        """
        Main method that encrypts the query string, hashes it, sends the request, and displays the
        JSON response sent by AllBet API.
        """
        try:
            secure_random_number = secrets.randbits(32) # 32-bit random integer
            query_string = "agent=" + self.agent_name + "&random=" + str(secure_random_number)

            data_string = self.threeDES(query_string)
            sign_string = self.md5(data_string)

            # Create encoded URL parameters.
            req_params = {}
            req_params["propertyId"] = self.AB_PROPERTY_ID
            req_params["data"] = data_string
            req_params["sign"] = sign_string
            encoded_params = urllib.parse.urlencode(req_params)

            url = self.endpoint + '?' + encoded_params
            response = requests.get(url)

            if response.status_code == 200:
                logger.info("AllBet Encryption Success")
                return HttpResponse(json.dumps(response.json()), content_type='application/json')
            else:
                return HttpResponse(response)

        except Exception as e:
            logger.error("AllBet EncryptionView Error: " + str(e))
            return HttpResponse("Error in encryption: " + str(e))


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
            logger.error("AllBet BalanceView Error: User " + str(player_account_name) + " does not exist.")
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
            logger.error("Generic AllBet BalanceView Error: " + str(e))
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


def place_bet(client, transaction_id, amount, bet_details):
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
            logger.error("AllBet TransferView Error: Bet transaction ID already used.")
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
            logger.error("AllBet TransferView Error: Single bet amount cannot be less than or equal to 0.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
        
        bet_details_total_amount += single_bet_amount

    if bet_details_total_amount != amount:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Total bet amount does not add up to the bet amounts in details parameter."
        }
        logger.error("AllBet TransferView Error: Total bet amount does not add up to the bet amounts in details parameter.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    # Illegal operation: total bet amount is 0 or negative.
    if float(amount) <= 0:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Total bet amount cannot be less than or equal to 0."
        }
        logger.error("AllBet TransferView Error: Total bet amount cannot be less than or equal to 0.")
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
                    user_balance = int(user_obj.main_wallet * 100) / 100.0
                    balance_after_placing = user_balance - single_bet_amount
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
                            "transaction_id": transaction_id
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
            logger.error("AllBet TransferView Error: User does not have enough money to place bet.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
    
    except Exception as e:
        if str(e) == "CustomUser matching query does not exist.":
            json_to_return = {
                "error_code": 10003,
                "message": "Specified user does not exist."
            }
            logger.error("AllBet TransferView Error: Specified user does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        logger.error("AllBet TransferView Error: Unspecified error in place_bet function.")
        return HttpResponse(str(e))


def settle_bet(client, transaction_id, amount, settle_details):
    """
    Helper method for the settle bet transfer type. 'amount' parameter will be positive for wins and negative for losses.
    This method supports batch settling of bets.
    """

    # Idempotence - check if transaction_id already used.
    try:
        existing_transactions = GameBet.objects.filter(other_data__transaction_id=transaction_id)

        if existing_transactions.count() >= 1:
            json_to_return = {
                "error_code": 10007,
                "message": "Error: transaction ID already used."
            }
            logger.error("AllBet TransferView Error: Cannot settle since Transaction ID is already used.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')
    except:
        pass

    settle_details_total_amount = 0

    for settle_dictionary in settle_details:
        settle_details_total_amount += settle_dictionary["amount"]
        single_settle_id = settle_dictionary["betNum"]

        try:
            existing_transaction = GameBet.objects.get(ref_no=single_settle_id)
        except ObjectDoesNotExist:
            json_to_return = {
                "error_code": 10006,
                "message": "Error: Attempted to settle a bet that does not exist."
            }
            logger.error("AllBet TransferView Error: Attempted to settle a bet that does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    if settle_details_total_amount != amount:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Total settle amount does not add up to the settle amount in details parameter."
        }
        logger.error("AllBet TransferView Error: Total settle amount does not add up to the settle amount in details parameter.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    try:
        user_obj = CustomUser.objects.get(username=client)
        user_balance = int(user_obj.main_wallet * 100) / 100.0

        # Loop through settle_details and settle bets individually.
        for settle_entry in settle_details:
            single_settle_id = settle_entry["betNum"]
            single_settle_amount = settle_entry["amount"]

            with transaction.atomic():
                user_balance = int(user_obj.main_wallet * 100) / 100.0
                balance_after_settling = user_balance + single_settle_amount
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
                        "transaction_id": transaction_id
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
            logger.error("AllBet TransferView Error: Specified user does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')

        logger.error("AllBet TransferView Error: Unspecified error in settle_bet function.")
        return HttpResponse(str(e))


#########################################################################################################################################################


def cancel_bet(client, transaction_id, amount, cancel_details):

    try:
        existing_transactions = GameBet.objects.filter(other_data__transaction_id=transaction_id)

        if existing_transactions.count() >= 1:
            json_to_return = {
                "error_code": 10007,
                "message": "Error: transaction ID already used."
            }
            logger.error("AllBet TransferView Error: Cannot cancel since Transaction ID is already used.")
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
        logger.error("AllBet TransferView Error: Specified user does not exist.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')

    
    if amount < 0:
        json_to_return = {
            "error_code": 40000,
            "message": "Cannot have negative total bet amount"
        }
        logger.error("AllBet TransferView Error: Cannot have negative total bet amount")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')





    cancel_details_total_amount = 0

    for cancel_dictionary in cancel_details:
        cancel_details_total_amount += cancel_dictionary["amount"]
        single_cancel_id = cancel_dictionary["betNum"]



        if cancel_dictionary["amount"] < 0:
            json_to_return = {
                "error_code": 40000,
                "message": "Error: Negative bet amount in details."
            }
            logger.error("AllBet TransferView Error: Negative bet amount in details.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')


        try:
            existing_transaction = GameBet.objects.get(ref_no=single_cancel_id)
        except ObjectDoesNotExist:
            json_to_return = {
                "error_code": 10006,
                "message": "Error: Attempted to cancel a bet that does not exist."
            }
            logger.error("AllBet TransferView Error: Attempted to cancel a bet that does not exist.")
            return HttpResponse(json.dumps(json_to_return), content_type='application/json')



    if cancel_details_total_amount != amount:
        json_to_return = {
            "error_code": 40000,
            "message": "Error: Total cancel amount does not add up to the cancel amount in details parameter."
        }
        logger.error("AllBet TransferView Error: Total cancel amount does not add up to the cancel amount in details parameter.")
        return HttpResponse(json.dumps(json_to_return), content_type='application/json')





#########################################################################################################################################################


class TransferView(View):

    def post(self, request, *args, **kwargs):
        """
        Partner Public Platform API that handles different wallet transfer types such as bet, cancel, settle,
        and re-settle. JSON is the data format that this endpoint receives and responds with.
        """
        try:
            json_data = json.loads(request.body)

            client = json_data["client"]
            transaction_id = json_data["tranId"]
            amount = json_data["amount"]
            currency = json_data["currency"]
            transfer_type = json_data["transferType"]
            bet_details = json_data["details"]
            
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

            # Default JSON Response fields
            res_error_code = 50000
            res_message = "server error"
            res_balance = 0

            # Place bet
            if transfer_type == 10:
                return place_bet(client, transaction_id, amount, bet_details)

            # Settle bet
            elif transfer_type == 20:
                return settle_bet(client, transaction_id, amount, bet_details)

            # Cancel bet
            elif transfer_type == 11:
                return cancel_bet(client, transaction_id, amount, bet_details)

            # Re-settle bet
            elif transfer_type == 21:
                pass # TODO

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
            logger.error("Generic AllBet TransferView Error: " + str(e))
            json_to_return = {
                                "error_code": 50000,
                                "message": "server error: " + str(e),
                                "balance": 0
                             }
            return JsonResponse(json_to_return)
