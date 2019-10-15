from django.views import View
from django.http import HttpResponse
from rest_framework.exceptions import ParseError
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

            # TODO: authentication logic. We'll use dummy data for now.

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
