from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from users.models import  CustomUser
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
import simplejson as json
from games.models import FGSession, Game, GameBet, GameProvider, Category
import xmltodict
from django.db import transaction
import decimal,random
import requests,json
import logging
from utils.constants import *
import decimal,re, math
import datetime
from datetime import date
from django.utils import timezone
from rest_framework.authtoken.models import Token

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
               
                user = Token.objects.get(key=token).user
                
            
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
                                    "@balance" :  math.floor(float(user.main_wallet * 100)) ,
                                    "@bonusbalance" :math.floor(float(user.bonus_wallet  * 100)) ,
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
            
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
            
                user = Token.objects.get(key=token).user
                # user = CustomUser.objects.get(username=mguser.user)   
                response = {
                    "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@token" : token,
                                "@balance" : math.floor(float(user.main_wallet * 100)) ,
                                "@bonusbalance" : math.floor(float(user.bonus_wallet  * 100)),
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

        elif name == "play":
            try:
                other_data = dict(dd)
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
        
                user = Token.objects.get(key=token).user
               
                provider = GameProvider.objects.get(provider_name=MG_PROVIDER)
                category = Category.objects.get(name='Games')
                transactionId = re.sub("[^0-9]", "", timestamp)
            
                if (playtype == "win" or playtype == "progressivewin" or playtype == "refund" or playtype == "transferfrommgs") :
                    wallet = user.main_wallet + decimal.Decimal(amount)/100
                
                else :
                    wallet = user.main_wallet - decimal.Decimal(amount)/100
                    
                if (wallet > 0):
                    with transaction.atomic():
                        user.main_wallet = wallet
                        user.save()
                        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))

                        if (playtype == "win" or playtype == "progressivewin" or playtype == "refund" or playtype == "transferfrommgs") :
                            GameBet.objects.get_or_create(provider=provider,
                                                            category=category,
                                                            user=user,
                                                            user_name=user.username,
                                                            amount_wagered=0.00,
                                                            currency=user.currency,
                                                            amount_won=decimal.Decimal(amount)/100,
                                                            market=ibetCN,
                                                            ref_no=transactionId,
                                                            transaction_id=trans_id,
                                                            other_data=other_data
                                                            )
                        else :
                            GameBet.objects.get_or_create(provider=provider,
                                                            category=category,
                                                            user=user,
                                                            user_name=user.username,
                                                            amount_wagered=decimal.Decimal(amount)/100,
                                                            currency=user.currency,
                                                            market=ibetCN,
                                                            ref_no=transactionId,
                                                            transaction_id=trans_id,
                                                            other_data=other_data
                                                            )

                    response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@token" : token,
                                    "@balance" : math.floor(float(user.main_wallet * 100)),
                                    "@bonusbalance" : math.floor(float(user.bonus_wallet  * 100)),
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


        elif name == "awardbonus":
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
                # bonus here should add more work later...
        
                user = Token.objects.get(key=token).user
                 
                response = {
                    "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@balance" : math.floor(float(user.main_wallet * 100)) ,
                                "@bonusbalance" : math.floor(float(user.bonus_wallet  * 100)),
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

        elif name == "endgame":
            try:
                # dd = xmltodict.parse(data)
                name = dd['pkt']['methodcall']['@name']
                timestamp = dd['pkt']['methodcall']['@timestamp']
                loginname = dd['pkt']['methodcall']['auth']['@login']
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
        
                user = Token.objects.get(key=token).user
                
                response = {
                    "pkt" : {
                        "methodresponse" : {
                            "@name" : name,
                            "@timestamp" : timestamp,
                            "result" : {
                                "@seq" : seq,
                                "@token" : token,
                                "@balance" : math.floor(float(user.main_wallet * 100)) ,
                                "@bonusbalance" : math.floor(float(user.bonus_wallet  * 100)),
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
