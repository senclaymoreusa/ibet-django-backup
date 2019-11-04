# Django
from django.views import View
from django.http import HttpResponse

# iBet
from utils.constants import *
from utils.aws_helper import getThirdPartyKeys

# Libraries
import json
import logging
import base64
import hashlib
import secrets
import urllib
import requests
import pyDes

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
