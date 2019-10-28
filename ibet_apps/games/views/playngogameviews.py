from django.views import View
from django.http import HttpResponse
from rest_framework.exceptions import ParseError

from users.models import CustomUser

import xmltodict

class AuthenticateView(View):

    def post(self, request, *args, **kwargs):
        """
        The Authenticate call makes a request to the Operator Account System to validate the
        user information upon the start of a new game. XML is the data format that this endpoint
        receives and responds with.
        """

        data = request.body

        try:
            # Extract data fields from request XML
            req_dict = xmltodict.parse(data)

            username = req_dict['authenticate']['username']
            product_id = req_dict['authenticate']['productId']
            client_ip = req_dict['authenticate']['clientIP']
            context_id = req_dict['authenticate']['contextId']
            access_token = req_dict['authenticate']['accessToken']
            language = req_dict['authenticate']['language']
            game_id = req_dict['authenticate']['gameId']
            channel = req_dict['authenticate']['channel']

            # print(username, product_id, client_ip, context_id, access_token, language, game_id, channel)

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
        The Balance call makes a request to the Operator Account System to get the user account 
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

            print(username, product_id, currency, game_id, access_token)

            #user = CustomUser.objects.get(pk=username)
            user_balance, user_currency, status_code = 1, 2, 3
            
            user = CustomUser.objects.get(username=username)
            user_balance = decimal.Decimal(user.main_wallet).quantize(decimal.Decimal('0.00'))
            user_currency = user.currency
            status_code = 0

            if user.block is True:
                status_code = 5
            if user.currency != currency:
                status_code = 3

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
            return HttpResponse(res_msg, content_type='text/xml') # Successful response


        except:
            print("Error in BalanceView")
