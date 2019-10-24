from django.views import View
from django.http import HttpResponse

import logging
import base64
import hashlib
import secrets
import urllib
import requests
from des import DesKey

logger = logging.getLogger('django')

class EnquireHandicapView(View):
    """
    This class is used to test DES encryption and Md5 signing, which is necessary for all requests to test
    the AllBet API as part of the 'Test Plan on API Integration Test' to be submitted to AllBet's QA
    Department for verification.

    https://www.abgintegration.com/swl/en/?chapter=1&page=2
    https://www.abgintegration.com/swl/en/?chapter=2&page=3_1
    """

    def get(self, request, *args, **kwargs):
        """
        Overview
        (1) Build query string
        (2) Encrypt query string using DES
        (3) Create sign parameter using Md5
        (4) Set propertyId & data parameters of request
        (5) Send request and verify response
        """
        try:
            # Hardcode for now; move to constants later.
            property_id = "2615593"
            des_key = "KH8hS7tG/hi/EjpQuReZ6kj/fSOvfLOS"
            md5_key = "gu7rCKSdumZ2bcChb1PgonDMtzh90mdRd9snXcquHi0="

            secure_random_number = secrets.randbits(32) # 32-bit random integer

            # Build query string
            query_string = "agent=fftrwa&random=" + str(secure_random_number)
            print("query_string: " + query_string)

            # Convert base64 to bytes 
            decoded_key = base64.b64decode(des_key)
            print("decoded_key: " + str(decoded_key))

            # Encrypt the query string using DES key provided by AllBet
            des_key = DesKey(decoded_key)
            print("des_key.is_single(): " + str(des_key.is_single()))
            print("des_key.is_triple(): " + str(des_key.is_triple()))

            byte_query_string = str.encode(query_string)
            print("byte_query_string: " + str(byte_query_string))

            encrypted_query_string = des_key.encrypt(byte_query_string, padding=True)
            print("encrypted_query_string: " + str(encrypted_query_string))

            # Convert encrypted_query_string back to base64 string
            data_bytes = base64.b64encode(encrypted_query_string)
            print("data_bytes: " + str(data_bytes))
            data = data_bytes.decode()
            print("data: " + data)




            ### 3des encryption done at this point




            string_to_sign = data + md5_key
            print("string_to_sign: " + string_to_sign)


            # Convert string_to_sign to bytes, do some md5 signing, convert resulting byte array back to base64 string
            bytes_string_to_sign = base64.b64decode(string_to_sign)
            print("bytes_string_to_sign: " + str(bytes_string_to_sign))

            hash_result = hashlib.md5(bytes_string_to_sign) 
            print(hash_result)
            byte_result = hash_result.digest()
            print("byte_result: " + str(byte_result))



            # convert bytes to base 64 string
            sign_bytes = base64.b64encode(byte_result) # Convert sign bytes to base 64
            print("sign: " + str(sign_bytes))
            sign_string = sign_bytes.decode() # byte to str
            print("sign_string: " + sign_string)



            ### all encryption done at this point??? maybe
            req_params = {}
            req_params["propertyId"] = property_id
            req_params["data"] = data
            req_params["sign"] = sign_string

            encoded_params = urllib.parse.urlencode(req_params)

            print("encoded_params: " + encoded_params)

            url = 'https://platform-api.apidemo.net:8443/query_agent_handicaps' + '?' + encoded_params

            print("url: " + url)


            res = requests.get(url)
            if res.status_code == 200:
                return HttpResponse(json.dumps(res.json()), content_type='application/json')
            else:
                return HttpResponse(res)






        except Exception as e:
            print(e)
            return HttpResponse("Error in encryption")