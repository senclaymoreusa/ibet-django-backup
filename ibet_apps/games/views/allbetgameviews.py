from django.views import View
from django.http import HttpResponse

import logging
import base64
import hashlib
import secrets
import urllib
import requests
import pyDes
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
            print("")
            # Hardcode for now; move to constants later.
            property_id = "2615593"
            des_key = "KH8hS7tG/hi/EjpQuReZ6kj/fSOvfLOS" # base64 string
            md5_key = "gu7rCKSdumZ2bcChb1PgonDMtzh90mdRd9snXcquHi0=" # base64 string
            base64_iv = "AAAAAAAAAAA=" # base64 string

            secure_random_number = secrets.randbits(32) # 32-bit random integer

            # Build query string
            query_string = "agent=ftrwaa&random=" + str(secure_random_number)
            print("query_string: " + query_string)

            # Convert provided encryption key from base64 to bytes 
            byte_key = base64.b64decode(des_key)
            print("byte_key: " + str(byte_key))

            # Convert provided IV from base64 to bytes 
            byte_iv = base64.b64decode(base64_iv)
            print("byte_iv: " + str(byte_iv))

            # Convert url to bytes
            byte_query_string = query_string.encode()
            print("byte_query_string: " + str(byte_query_string))
            
            des_obj = pyDes.triple_des(byte_key, pyDes.CBC, byte_iv, pad=None, padmode=pyDes.PAD_PKCS5)
            encrypted_msg = des_obj.encrypt(byte_query_string)

            print("Encrypted message: %r" % encrypted_msg)
            print("Decrypted message: %r" % des_obj.decrypt(encrypted_msg))

            # Convert encrypted_msg (bytes) to base64 string
            data_bytes = base64.b64encode(encrypted_msg)
            print("data_bytes: " + str(data_bytes))
            data_string = data_bytes.decode()
            print("data_string: " + data_string)
            print("")



            ### 3DES encryption done at this point

            string_to_sign = data_string + md5_key
            print("string_to_sign: " + string_to_sign)

            hashed_result = hashlib.md5(string_to_sign.encode())
            byte_result = hashed_result.digest()
            print("byte_result: " + str(byte_result))

            # Convert byte_result to base64 string
            sign_bytes = base64.b64encode(byte_result)
            print("sign_bytes: " + str(sign_bytes))
            sign_string = sign_bytes.decode()
            print("sign_string: " + sign_string)














            data = "test"
            sign_string = "test"


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