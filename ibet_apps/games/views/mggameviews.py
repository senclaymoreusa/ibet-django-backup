from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
import simplejson as json
from games.models import FGSession, MGToken
import xmltodict
import decimal
import requests,json
import logging
from utils.constants import *
import decimal,re, math

logger = logging.getLogger("django")

MG_RESPONSE_ERROR = {
    "6001" : "The player token is invalid.",
    "6002" : "The player token expired.",
    "6101" : "Login validation failed. Login name or password is incorrect.",
    "6102" : "Account is locked.",
    "6103" : "Account does not exist.",
    "6111" : "Account is blacklisted.",
    "6503" : "Player has insufficient funds.",
   
}

def parse_data(data):
    try: 
        dd = xmltodict.parse(data)
        return dd
    except Exception as e:
        logger.error("MG parse data Error: " + str(e))
        return None
            

class MGLogin(APIView):

    permission_classes = (AllowAny, )
    def post(self, request, *args, **kwargs):
        data = request.body
        # print(data)
        dd = parse_data(data)
        if (dd is None):
            return HttpResponse("MG parse data Error", status=status.HTTP_400_BAD_REQUEST)
        try:
            name = dd['pkt']['methodcall']['@name']
            timestamp = dd['pkt']['methodcall']['@timestamp']
            loginname = dd['pkt']['methodcall']['auth']['@login']
            seq = dd['pkt']['methodcall']['call']['@seq']
            token = dd['pkt']['methodcall']['call']['@token']
        except Exception as e:
            logger.error("MG parse data Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        # print(name)
        try:
            mguser = MGToken.objects.get(token=token)
            user = CustomUser.objects.get(username=mguser.user)   
          

            response = {
                    "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@token" : token,
                                "@loginname" : user.username,
                                "@currency" : CURRENCY_CHOICES[user.currency][1],
                                "@country" : user.country,
                                "@city" : user.city,
                                "@balance" : user.main_wallet,
                                "@bonusbalance" : user.bonus_wallet ,
                                "@wallet" : "vanguard",
                                "extinfo" : {}
                            },
                            
                        }
                    }
            }
        except:
            response = {
                "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@errorcode" : "6103",
                                "@errordescription": MG_RESPONSE_ERROR["6103"],
                                "extinfo" : {}
                            },
                            
                        }
                    }
            }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')

class GetBalance(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):   
        data = request.body
        #print(data)
        dd = parse_data(data)
        if (dd is None):
            return HttpResponse("MG parse data Error", status=status.HTTP_400_BAD_REQUEST)
        try:
            name = dd['pkt']['methodcall']['@name']
            timestamp = dd['pkt']['methodcall']['@timestamp']
            loginname = dd['pkt']['methodcall']['auth']['@login']
            seq = dd['pkt']['methodcall']['call']['@seq']
            token = dd['pkt']['methodcall']['call']['@token']
        except Exception as e:
            logger.error("MG parse data Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        try:
            mguser = MGToken.objects.get(token=token)
            user = CustomUser.objects.get(username=mguser.user)   
            response = {
                "pkt" : {
                    "methodresponse" : {
                        "@name" : name,
                        "@timestamp" : timestamp,
                        "result" : {
                            "@seq" : seq,
                            "@token" : token,
                            "@balance" : user.main_wallet,
                            "@bonusbalance" : user.bonus_wallet,
                            "extinfo" : {}
                        },
                        
                    }
                }
            }
        except:
            response = {
                "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@errorcode" : "6103",
                                "@errordescription": MG_RESPONSE_ERROR["6103"],
                                "extinfo" : {}
                            },
                            
                        }
                    }
            }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')

class Play(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):   
        data = request.body
        dd = parse_data(data)
        if (dd is None):
            return HttpResponse("MG parse data Error", status=status.HTTP_400_BAD_REQUEST)
        try:
            name = dd['pkt']['methodcall']['@name']
            timestamp = dd['pkt']['methodcall']['@timestamp']
            loginname = dd['pkt']['methodcall']['auth']['@login']
            seq = dd['pkt']['methodcall']['call']['@seq']
            token = dd['pkt']['methodcall']['call']['@token']
            playtype = dd['pkt']['methodcall']['call']['@playtype']
            amount = dd['pkt']['methodcall']['call']['@amount']
        except Exception as e:
            logger.error("MG parse data Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        # here should judge the currency later...
        try:
            mguser = MGToken.objects.get(token=token)
            user = CustomUser.objects.get(username=mguser.user)  
           
            if (playtype == "win" or playtype == "progressivewin" or playtype == "refund" or playtype == "transferfrommgs") :
                wallet = user.main_wallet + decimal.Decimal(amount)/100
              
            else :
                wallet = user.main_wallet - decimal.Decimal(amount)/100
                
            if (wallet > 0):
                user.main_wallet = wallet
                user.save()
                response = {
                "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@token" : token,
                                "@balance" : user.main_wallet,
                                "@bonusbalance" : user.bonus_wallet,
                                "@exttransactionid" : re.sub("[^0-9]", "", timestamp),
                                "extinfo" : {}
                            },
                        }
                    }
                } 
            else :
                response = {
                "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@errorcode" : "6503",
                                "@errordescription" : MG_RESPONSE_ERROR["6503"],
                                "extinfo" : {}
                            },
                        }
                    }
                } 
        except:
            response = {
                "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@errorcode" : "6103",
                                "@errordescription": MG_RESPONSE_ERROR["6103"],
                                "extinfo" : {}
                            },
                            
                        }
                    }
            }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')

class AwardBonus(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):   
        data = request.body
        dd = parse_data(data)
        if (dd is None):
            return HttpResponse("MG parse data Error", status=status.HTTP_400_BAD_REQUEST)
        try:
            name = dd['pkt']['methodcall']['@name']
            timestamp = dd['pkt']['methodcall']['@timestamp']
            loginname = dd['pkt']['methodcall']['auth']['@login']
            seq = dd['pkt']['methodcall']['call']['@seq']
            token = dd['pkt']['methodcall']['call']['@token']
        except Exception as e:
            logger.error("MG parse data Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        # bonus here should add more work later...
        try:
            mguser = MGToken.objects.get(token=token)
            user = CustomUser.objects.get(username=mguser.user)   
            response = {
                "pkt" : {
                    "methodresponse" : {
                        "@name" : name,
                        "@timestamp" : timestamp,
                        "result" : {
                            "@seq" : seq,
                            "@balance" : user.main_wallet,
                            "@bonusbalance" : user.bonus_wallet,
                            "@exttransactionid" : re.sub("[^0-9]", "", timestamp),
                            "extinfo" : {}
                        },
                        
                    }
                }
            }
        except:
            response = {
                "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@errorcode" : "6103",
                                "@errordescription": MG_RESPONSE_ERROR["6103"],
                                "extinfo" : {}
                            },
                            
                        }
                    }
            }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')

class EndGame(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):   
        data = request.body
        dd = parse_data(data)
        if (dd is None):
            return HttpResponse("MG parse data Error", status=status.HTTP_400_BAD_REQUEST)
        try:
            name = dd['pkt']['methodcall']['@name']
            timestamp = dd['pkt']['methodcall']['@timestamp']
            loginname = dd['pkt']['methodcall']['auth']['@login']
            seq = dd['pkt']['methodcall']['call']['@seq']
            token = dd['pkt']['methodcall']['call']['@token']
        except Exception as e:
            logger.error("MG parse data Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        try:
            mguser = MGToken.objects.get(token=token)
            user = CustomUser.objects.get(username=mguser.user)  
            response = {
                "pkt" : {
                    "methodresponse" : {
                        "@name" : name,
                        "@timestamp" : timestamp,
                        "result" : {
                            "@seq" : seq,
                            "@token" : token,
                            "@balance" : user.main_wallet,
                            "@bonusbalance" : user.bonus_wallet,
                            "extinfo" : {}
                        },
                        
                    }
                }
            }
        except:
            response = {
                "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@errorcode" : "6103",
                                "@errordescription": MG_RESPONSE_ERROR["6103"],
                                "extinfo" : {}
                            },
                            
                        }
                    }
            }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')

class RefreshToken(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):   
        data = request.body
        # print(data)
        dd = parse_data(data)
        if (dd is None):
            return HttpResponse("MG parse data Error", status=status.HTTP_400_BAD_REQUEST)
        try:
            name = dd['pkt']['methodcall']['@name']
            timestamp = dd['pkt']['methodcall']['@timestamp']
            loginname = dd['pkt']['methodcall']['auth']['@login']
            seq = dd['pkt']['methodcall']['call']['@seq']
            token = dd['pkt']['methodcall']['call']['@token']
        except Exception as e:
            logger.error("MG parse data Error: " + str(e))
            return HttpResponse(str(e), status=status.HTTP_400_BAD_REQUEST)
        #more work need here...
        response = {
            "pkt" : {
                "methodresponse" : {
                    "@name" : name,
                    "@timestamp" : timestamp,
                    "result" : {
                        "@seq" : seq,
                        "@token" : token,
                        "extinfo" : {}
                    },
                    
                }
            }
        }
        res = xmltodict.unparse(response, pretty=True)
        return HttpResponse(res, content_type='text/xml')