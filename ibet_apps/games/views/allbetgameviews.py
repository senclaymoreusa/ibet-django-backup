from django.views import View
from django.http import HttpResponse

import logging
import secrets # Used for generating secure random numbers
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
        (3) Set propertyId & data parameters of request
        (4) Create sign parameter using Md5
        (5) Send request and verify response
        """
        try:
            # Hardcode for now; move to constants later.
            property_id = "2615593"
            des_key = "KH8hS7tG/hi/EjpQuReZ6kj/fSOvfLOS"
            md5_key = "gu7rCKSdumZ2bcChb1PgonDMtzh90mdRd9snXcquHi0="

            secure_random_number = secrets.randbits(32) # 32-bit random integer

            query_string = "agent=fftrwa&random=" + str(secure_random_number)
            print(query_string)

            # Encrypt the query string using DES key provided by AllBet
            key = DesKey(b"KH8hS7tG/hi/EjpQuReZ6kj/fSOvfLOS")
            print("key.is_single(): " + str(key.is_single()))
            print("key.is_triple(): " + str(key.is_triple()))

        except Exception as e:
            print(e)
            return HttpResponse("Error in encryption")