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
    "6003" : "The authentication credentials for the API are incorrect.",
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
        try:
            name = dd['pkt']['methodcall']['@name']
            apiusername = dd['pkt']['methodcall']['auth']['@login']
            apipassword = dd['pkt']['methodcall']['auth']['@password']
            timestamp = dd['pkt']['methodcall']['@timestamp']
            seq = dd['pkt']['methodcall']['call']['@seq']
            
        except Exception as e:
            logger.critical("FATAL__ERROR: MG parse data Error - " + str(e))
            response = {
                        "pkt" : {
                            "methodresponse" : {
                                "@name" : "",
                                "@timestamp" : "",
                                "result" : {
                                    "@seq" : "",
                                    "@errorcode" : "6000",
                                    "@errordescription": MG_RESPONSE_ERROR["6000"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
            }
            res = xmltodict.unparse(response, pretty=True)
            return HttpResponse(res, content_type='text/xml')

        # api security check
        if apiusername != USERNAME or apipassword != PASSWORD:
            logger.critical("FATAL__ERROR: The authentication credentials for the API are incorrect.")
            response = {
                "pkt" : {
                    "methodresponse" : {
                        "@name" : name,
                        "@timestamp" : timestamp,
                        "result" : {
                            "@seq" : seq,
                            "@errorcode" : "6003",
                            "@errordescription": MG_RESPONSE_ERROR["6003"],
                            "extinfo" : {}
                        },
                                
                    }
                        
                }
            }
            res = xmltodict.unparse(response, pretty=True)
            return HttpResponse(res, content_type='text/xml')
        
        if name == "login":
            try:            
                # timestamp = dd['pkt']['methodcall']['@timestamp']
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
                logger.critical("FATAL__ERROR: MG invalid user in Login: ", e)
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6001",
                                    "@errordescription": MG_RESPONSE_ERROR["6001"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')
            except Exception as e:
                logger.critical("FATAL__ERROR: MG parse data Error in Login: " + str(e))
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
                logger.critical("FATAL__ERROR: MG invalid user in getbalance: ", e)
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6001",
                                    "@errordescription": MG_RESPONSE_ERROR["6001"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except Exception as e:
                logger.critical("FATAL__ERROR: MG parse data Error in getbalance: " + str(e))
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
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
                playtype = dd['pkt']['methodcall']['call']['@playtype']
                amount = dd['pkt']['methodcall']['call']['@amount']
                currency = dd['pkt']['methodcall']['call']['@currency']
                gameid = dd['pkt']['methodcall']['call']['@gameid']
                actionid = dd['pkt']['methodcall']['call']['@actionid']
                # gameref = dd['pkt']['methodcall']['call']['@gamereference']
               
                # here should judge the currency later...
        
                user = Token.objects.get(key=token).user
               
                provider = GameProvider.objects.get(provider_name=MG_PROVIDER)
                category = Category.objects.get(name='Games')
                transactionId = re.sub("[^0-9]", "", timestamp)
                samePack = False
                if (playtype == "win" or playtype == "progressivewin" or playtype == "refund" or playtype == "transferfrommgs") :
                    # same win package exist
                    try:
                        bet = GameBet.objects.filter(other_data=actionid, ref_no=gameid)
                        if bet.count() > 0:
                            wallet = user.main_wallet
                            samePack = True
                        else :
                            wallet = user.main_wallet + decimal.Decimal(amount)/100
                    except:
                        wallet = user.main_wallet + decimal.Decimal(amount)/100
                
                else :
                    # same bet package exist
                    try:
                        bet = GameBet.objects.filter(other_data=actionid, ref_no=gameid)
                        if bet.count() > 0:
                            wallet = user.main_wallet
                            samePack = True
                        else :
                            wallet = user.main_wallet + decimal.Decimal(amount)/100
                    except:
                        wallet = user.main_wallet - decimal.Decimal(amount)/100
                    
                if (wallet > 0):
                    with transaction.atomic():
                        user.main_wallet = wallet
                        user.save()
                        trans_id = user.username + "-" + timezone.datetime.today().isoformat() + "-" + str(random.randint(0, 10000000))
                        
                        if (playtype == "win" or playtype == "progressivewin") :
                            if (not samePack):
                                GameBet.objects.get_or_create(provider=provider,
                                                                category=category,
                                                                user=user,
                                                                user_name=user.username,
                                                                amount_wagered=0.00,
                                                                currency=user.currency,
                                                                amount_won=decimal.Decimal(amount)/100,
                                                                market=ibetCN,
                                                                ref_no=gameid,
                                                                transaction_id=trans_id,
                                                                resolved_time=timezone.now(),
                                                                # game_name=gameref,
                                                                outcome=0,
                                                                other_data=actionid
                                                                )
                        elif (playtype == "refund" or playtype == "transferfrommgs") :
                            if (not samePack):
                                GameBet.objects.get_or_create(provider=provider,
                                                                category=category,
                                                                user=user,
                                                                user_name=user.username,
                                                                amount_wagered=0.00,
                                                                currency=user.currency,
                                                                amount_won=decimal.Decimal(amount)/100,
                                                                market=ibetCN,
                                                                ref_no=gameid,
                                                                transaction_id=trans_id,
                                                                resolved_time=timezone.now(),
                                                                # game_name=gameref,
                                                                outcome=3,
                                                                other_data=actionid
                                                                )

                        else :
                            if (not samePack):
                                GameBet.objects.get_or_create(provider=provider,
                                                                category=category,
                                                                user=user,
                                                                user_name=user.username,
                                                                amount_wagered=decimal.Decimal(amount)/100,
                                                                currency=user.currency,
                                                                market=ibetCN,
                                                                ref_no=gameid,
                                                                transaction_id=trans_id,
                                                                # game_name=gameref,
                                                                other_data=actionid
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
                logger.critical("FATAL__ERROR: MG invalid user in play: ", e)
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6001",
                                    "@errordescription": MG_RESPONSE_ERROR["6001"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except Exception as e:
                logger.critical("FATAL__ERROR: MG parse data Error in play: " + str(e))
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
                logger.error("ERROR: MG invalid user: ", e)
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6001",
                                    "@errordescription": MG_RESPONSE_ERROR["6001"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except Exception as e:
                logger.error("ERROR: MG parse data Error: " + str(e))
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
                seq = dd['pkt']['methodcall']['call']['@seq']
                token = dd['pkt']['methodcall']['call']['@token']
                offline = dd['pkt']['methodcall']['call']['@offline']

                # add offline token.
                if offline == "true":
                    user = CustomUser.objects.get(username=token)
                else:
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
                logger.critical("FATAL__ERROR: MG invalid user: ", e)
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6001",
                                    "@errordescription": MG_RESPONSE_ERROR["6001"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except Exception as e:
                logger.critical("FATAL__ERROR: MG parse data Error: " + str(e))
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
                logger.critical("FATAL__ERROR: MG invalid user in token: ", e)
                response = {
                    "pkt" : {
                            "methodresponse" : {
                                "@name" : name,
                                "@timestamp" : timestamp,
                                "result" : {
                                    "@seq" : seq,
                                    "@errorcode" : "6001",
                                    "@errordescription": MG_RESPONSE_ERROR["6001"],
                                    "extinfo" : {}
                                },
                                
                            }
                        }
                }
                res = xmltodict.unparse(response, pretty=True)
                return HttpResponse(res, content_type='text/xml')

            except Exception as e:
                logger.critical("FATAL__ERROR: MG parse data Error: " + str(e))
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
