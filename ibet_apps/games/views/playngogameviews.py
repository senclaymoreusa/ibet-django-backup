# Django
from django.views import View
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError
from rest_framework import status
from django.db import transaction

# iBet
from users.models import CustomUser
from games.models import GameBet, GameProvider, Category
from utils.constants import *

# Libraries
import xmltodict
import logging
import decimal

logger = logging.getLogger('django')

class GameLaunchView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("GameLaunchView API")


class AuthenticateView(View):

    def post(self, request, *args, **kwargs):
        """
        When a PNG game is launched, a username (session token) is generated for the current user 
        and sent to the provider via a launch URL. The Authenticate API receives this session token 
        parameter and uses it to fetch the user associated with the session token. Next, a PNG 
        session object is created for the specific user in order to store information about a player's 
        game rounds.
        """

        try:
            # Extract data fields from request XML
            data = request.body
            req_dict = xmltodict.parse(data)

            session_token = req_dict['authenticate']['username']
            product_id = req_dict['authenticate']['productId']
            client_ip = req_dict['authenticate']['clientIP']
            context_id = req_dict['authenticate']['contextId']
            access_token = req_dict['authenticate']['accessToken']
            language = req_dict['authenticate']['language']
            game_id = req_dict['authenticate']['gameId']
            channel = req_dict['authenticate']['channel']

            # print(session_token, product_id, client_ip, context_id, access_token, language, game_id, channel)

            # TODO: authentication logic. Using dummy data for now.

            external_id = 554433 # Placeholder
            status_code = 0 # Placeholder
            status_message = "ok" # Placeholder
            user_currency = "EUR" # Placeholder
            nickname = "MaxPower" # Placeholder
            country = "SE" # Placeholder
            birthdate = "1970-01-01" # Placeholder
            registration = "2010-05-05" # Placeholder
            res_language = "EN" # Placeholder
            affiliate_id = "" # Placeholder
            real = 1234.56 # Placeholder
            external_game_session_id = "" # Placeholder
            region = 3 # Placeholder

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
                        "#text": user_currency
                    },
                    "nickname": {
                        "#text": nickname
                    },
                    "country": {
                        "#text": country
                    },
                    "birthdate": {
                        "#text": birthdate
                    },
                    "registration": {
                        "#text": registration
                    },
                    "language": {
                        "#text": res_language
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
                    "region": {
                        "#text": str(region)
                    },
                }
            }

            res_msg = xmltodict.unparse(res_dict, pretty=True)
            return HttpResponse(res_msg, content_type='text/xml') # Successful response

        except:
            # Malformed xml, missing tags, or error parsing data
            raise ParseError


class BalanceView(View):

    def post(self, request, *args, **kwargs):
        """
        The Balance call makes a request to the Operator Account System to retrieve the user account 
        balance available to transfer to a provider. XML is the data format that this endpoint
        receives and responds with.
        """
        
        data = request.body

        try:
            # Extract data fields from request XML
            req_dict = xmltodict.parse(data)

            username = req_dict['balance']['externalId']
            product_id = req_dict['balance']['productId']
            currency = req_dict['balance']['currency']
            game_id = req_dict['balance']['gameId']
            access_token = req_dict['balance']['accessToken']

            # TODO: Verify accessToken after it is provided by PLAY'nGO
            
            # Retrieve balance of specified user and set status code based on user account status
            user = CustomUser.objects.get(username=username)

            if user:
                # print("PLAY'nGO BalanceView: User " + username + " found!")
                logger.info("PLAY'nGO BalanceView: User " + username + " found!")
            else:
                # print("PLAY'nGO BalanceView: User " + username + " not found!")
                logger.error("PLAY'nGO BalanceView: User " + username + " not found!")

            user_balance = decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00'))
            user_currency = CURRENCY_CHOICES[user.currency][1]
            status_code = PNG_STATUS_OK # Default case is 0 (request successful)

            if user.block is True:
                status_code = PNG_STATUS_ACCOUNTLOCKED
            elif user.active is False:
                status_code = PNG_STATUS_ACCOUNTDISABLED
            elif user_currency != currency:
                status_code = PNG_STATUS_INVALIDCURRENCY

            # Compose response dictionary and convert to response XML
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

            res_msg = xmltodict.unparse(res_dict, pretty=True)
            return HttpResponse(res_msg, content_type='text/xml')

        except Exception as e:
            logger.error("PLAY'nGO BalanceView Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


class ReserveView(View):
    
    def post(self, request, *args, **kwargs):
        """
        The Reserve call makes a request to the Operator Account System to deduct a bet amount from
        the user's wallet. XML is the data format that this endpoint receives and responds with.
        """
        # TODO: Follow up with provider about special case where a bet amount of 0.00 is allowed.

        data = request.body

        try:
            # Extract data fields from request XML
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
            
            user = CustomUser.objects.get(username=username)
            user_balance = decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00'))
            bet_amount_decimal = decimal.Decimal(bet_amount_str).quantize(decimal.Decimal('0.00'))
            user_currency_text = CURRENCY_CHOICES[user.currency][1]

            status_code = PNG_STATUS_OK
            PROVIDER = GameProvider.objects.get(provider_name="PLAYNGO")
            CATEGORY = Category.objects.get(name="SLOTS")

            #print("")
            #print(type(user_balance))
            #print(str(user_balance))
            #print(type(bet_amount_decimal))
            #print(str(bet_amount_decimal))
            #print("req_currency: " + req_currency)
            #print("user.currency: " + str(user.currency))
            #print("user_currency_text: " + user_currency_text)
            #print("")

            # Checking currency type takes priority over making a bet.
            if user_currency_text != req_currency:
                status_code = PNG_STATUS_INVALIDCURRENCY
                logger.error("PLAY'nGO ReserveView Error: Currency mismatch.")

            # Bet can go through. 
            elif user_balance >= bet_amount_decimal:
                with transaction.atomic():
                    balance_after_bet = user_balance - bet_amount_decimal
                    user.main_wallet = balance_after_bet
                    user.save()

                    # Create a GameBet entry upon successful placement of a bet.
                    GameBet.objects.create(
                        provider = PROVIDER,
                        category = CATEGORY,
                        #game = None,
                        #game_name = None,
                        username = user,
                        amount_wagered = bet_amount_decimal,
                        amount_won = 0.00,
                        #outcome = None,
                        #odds = None,
                        #bet_type = None,
                        #line = None,
                        currency = user_currency_text,
                        market = ibetVN, # Need to clarify with provider
                        ref_no = transaction_id,
                        #bet_time = None,
                        #resolved_time = None,
                        #other_data = {}
                    )

                    logger.info("PLAY'nGO ReserveView Success: Bet placed for user: " + user.username)

            else:
                status_code = PNG_STATUS_NOTENOUGHMONEY
                logger.error("PLAY'nGO ReserveView Error: Not enough money to place bet.")

            # Compose response dictionary and convert to response XML.
            res_dict = {
                "reserve": {
                    "real": {
                        # Cannot use balance_after_bet in case bet did not go through
                        "#text": str(decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')))
                    },
                    "currency": {
                        "#text": str(user_currency_text)
                    },
                    "statusCode": {
                        "#text": str(status_code)
                    },
                }
            }

            res_msg = xmltodict.unparse(res_dict, pretty=True)
            return HttpResponse(res_msg, content_type='text/xml')

        except Exception as e:
            logger.error("PLAY'nGO ReserveView Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)


class ReleaseView(View):

    def post(self, request, *args, **kwargs):
        """
        """
        data = request.body

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
            free_game_total_gain = req_dict['release']['freegameTotalGain']



            user = CustomUser.objects.get(username=username)
            user_balance = decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00'))
            win_amount_decimal = decimal.Decimal(win_amount_str).quantize(decimal.Decimal('0.00'))

            status_code = PNG_STATUS_OK

            # TODO: Check for invalid currency.

            balance_after_win = user_balance + win_amount_decimal
            user.main_wallet = balance_after_win
            user.save()



            res_dict = {
                "release": {
                    "real": {
                        "#text": str(decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00')))
                    },
                    "currency": {
                        "#text": ""
                    },
                    "statusCode": {
                        "#text": str(status_code)
                    },
                }
            }

            res_msg = xmltodict.unparse(res_dict, pretty=True)
            return HttpResponse(res_msg, content_type='text/xml')



        except Exception as e:
            logger.error("PLAY'nGO ReleaseView Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
