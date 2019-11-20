from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
import simplejson as json
from games.models import FGSession, MGToken, Game, GameBet, GameProvider, Category
import xmltodict
from django.db import transaction
import decimal
import requests,json
import logging
from utils.constants import *
import decimal,re, math

logger = logging.getLogger("django")

MG_RESPONSE_ERROR = {
    "6000" : "Unspecified error",
    "6001" : "The player token is invalid.",
    "6002" : "The player token expired.",
    "6101" : "Login validation failed. Login name or password is incorrect.",
    "6102" : "Account is locked.",
    "6103" : "Account does not exist.",
    "6111" : "Account is blacklisted.",
    "6503" : "Player has insufficient funds.",
   
}

# def parse_data(data):
#     try: 
#         dd = xmltodict.parse(data)
#         return dd
#     except Exception as e:
#         logger.error("MG parse data Error: " + str(e))
#         return None
class MGtoken(APIView):
    permission_classes = (AllowAny, )
    def get(self, request, *args, **kwargs):   
        pk = request.GET['pk']
        token = request.GET['token']  
       
        user = CustomUser.objects.get(pk=pk)
        try:
            mguser = MGToken.objects.get(user=user)
            mguser.token = token
            mguser.save()
            response = {
                "user token updated."
            }
        except:       
            MGToken.objects.create(user=user,token=token)  
            response = {
                "user token created."
            }     
        return HttpResponse(response,content_type='application/json',status=200)

class MGgame(APIView):

    permission_classes = (AllowAny, )
    def post(self, request, *args, **kwargs):
        data = request.body
        dd = xmltodict.parse(data)
        name = dd['pkt']['methodcall']['@name']

        if name == "login":
            try:            
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
            
        
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
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except ObjectDoesNotExist as e:
                logger.error("MG invalid user: ", e)
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
            except Exception as e:
                logger.error("MG parse data Error: " + str(e))
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6000",
                                    "@errordescription": MG_RESPONSE_ERROR["6000"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

        elif name == "getbalance":
       

# class GetBalance(APIView):
#     permission_classes = (AllowAny, )

#     def post(self, request, *args, **kwargs):   
#         data = request.body      
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
            
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
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except ObjectDoesNotExist as e:
                logger.error("MG invalid user: ", e)
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

            except Exception as e:
                logger.error("MG parse data Error: " + str(e))
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6000",
                                    "@errordescription": MG_RESPONSE_ERROR["6000"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

# class Play(APIView):
#     permission_classes = (AllowAny, )

#     def post(self, request, *args, **kwargs):   
#         data = request.body
        elif name == "play":
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
                playtype = dd['pkt']['methodcall']['call']['@playtype']
                amount = dd['pkt']['methodcall']['call']['@amount']
                currency = dd['pkt']['methodcall']['call']['@currency']
            
                # here should judge the currency later...
        
                mguser = MGToken.objects.get(token=token)
                user = CustomUser.objects.get(username=mguser.user)  
                transactionId = re.sub("[^0-9]", "", timestamp)
            
                if (playtype == "win" or playtype == "progressivewin" or playtype == "refund" or playtype == "transferfrommgs") :
                    wallet = user.main_wallet + decimal.Decimal(amount)/100
                
                else :
                    wallet = user.main_wallet - decimal.Decimal(amount)/100
                    
                if (wallet > 0):
                    with transaction.atomic():
                        user.main_wallet = wallet
                        user.save()
                        if (playtype == "win" or playtype == "progressivewin" or playtype == "refund" or playtype == "transferfrommgs") :
                            GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="MG"),
                                                            category=Category.objects.get(name='Slots'),
                                                            username=user,
                                                            amount_wagered=0.00,
                                                            currency=currency,
                                                            amount_won=decimal.Decimal(amount)/100,
                                                            market=ibetCN,
                                                            ref_no=transactionId
                                                            )
                        else :
                            GameBet.objects.get_or_create(provider=GameProvider.objects.get(provider_name="MG"),
                                                            category=Category.objects.get(name='Slots'),
                                                            username=user,
                                                            amount_wagered=decimal.Decimal(amount)/100,
                                                            currency=currency,
                                                            market=ibetCN,
                                                            ref_no=transactionId
                                                            )

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
                                    "@exttransactionid" : transactionId,
                                    "extinfo" : {}
                                },
                            }
                        }
                    } 
                    res = xmltodict.unparse(response, pretty=True)
                    return HttpResponse(res, content_type='text/xml')
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
                    res = xmltodict.unparse(response, pretty=True)
                    return HttpResponse(res, content_type='text/xml')

            except ObjectDoesNotExist as e:
                logger.error("MG invalid user: ", e)
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

            except Exception as e:
                logger.error("MG parse data Error: " + str(e))
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6000",
                                    "@errordescription": MG_RESPONSE_ERROR["6000"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')


# class AwardBonus(APIView):
#     permission_classes = (AllowAny, )

#     def post(self, request, *args, **kwargs):   
#         data = request.body
        elif name == "awardbonus":
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
                # bonus here should add more work later...
        
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
            except ObjectDoesNotExist as e:
                logger.error("MG invalid user: ", e)
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

            except Exception as e:
                logger.error("MG parse data Error: " + str(e))
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6000",
                                    "@errordescription": MG_RESPONSE_ERROR["6000"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

# class EndGame(APIView):
#     permission_classes = (AllowAny, )

#     def post(self, request, *args, **kwargs):   
#         data = request.body
        elif name == "endgame":
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
        
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
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except ObjectDoesNotExist as e:
                logger.error("MG invalid user: ", e)
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

            except Exception as e:
                logger.error("MG parse data Error: " + str(e))
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6000",
                                    "@errordescription": MG_RESPONSE_ERROR["6000"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

# class RefreshToken(APIView):
#     permission_classes = (AllowAny, )

#     def post(self, request, *args, **kwargs):   
#         data = request.body
        else :
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
        
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

            except ObjectDoesNotExist as e:
                logger.error("MG invalid user: ", e)
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

            except Exception as e:
                logger.error("MG parse data Error: " + str(e))
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6000",
                                    "@errordescription": MG_RESPONSE_ERROR["6000"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')
