from datetime import datetime

from django.contrib.auth import authenticate
from users.models import CustomUser
from rest_framework.authtoken.models import Token

import decimal
import logging
import games.n2_socket.n2_constants as const

logger = logging.getLogger("django")

class PlayerManagement:
    loginId = None
    vendorId = None
    passcode = ''

    def __init__(self, VendorId, Passcode):
        self.loginId = ""
        self.vendorId = VendorId
        self.passcode = Passcode
        self.currencyId = ""
        self.clientIp = None

    def ValidatePlayer(self, login, pw, method):
        if method == "login":
            user = authenticate(username=login, password=pw)
            if user:
                logger.info("User " + login + " found & authenticated...")
                self.currencyId = const.CURRENCY_MAP[user.currency]
                return (0, user)
            else:
                logger.info("User " + login + " not found!")
                return (105, None)    
        else:
            user = CustomUser.objects.get(username=login)
            if user:
                try:
                    sessionToken = Token.objects.get(user_id=user)
                    self.currencyId = const.CURRENCY_MAP[user.currency]
                    logger.info("User " + login + " found & session authenticated...")
                    return (0, user, sessionToken)
                except Exception as ex:
                    logger.info("No session token for this user")
                    return (105, user)
            else:
                logger.info("User " + login + " not found")
                return (105, None)

    def GetPlayerBalance(self, username, currencyId):
        user = CustomUser.objects.get(username=username)
        self.currencyId = currencyId
        if user:
            logger.info("User " + username + "'s balance retrieved")
            return (0, user)
        else:
            logger.info("User " + username +  " balance not found!")
            return (105, None)

    def ProcessLoginRequest(self, xmlDoc): # parse values out of xml request
        for root in xmlDoc.getchildren():
            for elem in root.getchildren():
                if not elem.text:
                    text = "None"
                else:
                    text = elem.text
                if elem.tag == "userid":
                    self.loginId = text
                elif elem.tag == "vendorid":
                    self.vendorId = text
                elif elem.tag == "password":
                    playerPassword = text

                # print(elem.tag + " => " + text)
        
        #validate the user Id here
        return self.ValidatePlayer(self.loginId, playerPassword, "login") # returns tuple (status, user)

    def ProcessWebLoginRequest(self, xmlDoc): # parse values out of xml request
            for root in xmlDoc.getchildren():
                for elem in root.getchildren():
                    if not elem.text:
                        text = "None"
                    else:
                        text = elem.text
                    if elem.tag == "userid":
                        self.loginId = text
                    elif elem.tag == "vendorid":
                        self.vendorId = text
                    elif elem.tag == "sessiontoken":
                        sessionToken = text
                    elif elem.tag == "clientip":
                        self.clientIp = text
                    # print(elem.tag + " => " + text)
            
            #validate the user Id here
            return self.ValidatePlayer(self.loginId, sessionToken, "session") # returns tuple (status, user, token)

    def ProcessGetBalance(self, xmlDoc):
        for root in xmlDoc.getchildren():
            for elem in root.getchildren():
                if not elem.text:
                    text = "None"
                else:
                    text = elem.text
                if elem.tag == "userid":
                    self.loginId = text
                if elem.tag == "vendorid":
                    self.vendorId = text
                if elem.tag == "currencyid":
                    currencyId = text
                
                # print(elem.tag + " => " + text)
        
        # retrieve user balance
        return self.GetPlayerBalance(self.loginId, currencyId) # returns tuple (status, user)

    def ProcessTradeRequest(self, xmlDoc, action):
        trades = [] # array of trade objects
        for root in xmlDoc.getchildren():
            for elem in root.getchildren():
                if not elem.text:
                    text = "None"
                else:
                    text = elem.text
                if elem.tag == "userid":
                    self.loginId = text
                if elem.tag == "vendorid":
                    self.vendorId = text
                if elem.tag == "totalamount":
                    totalamount = text
                # if elem.tag == "gameid":    bacarrat/roulette/blackjack
                #     gameid = text
                if elem.tag == "tradeid":
                    tradeid = text
                if elem.tag == 'trades':
                    for trade in elem.getchildren():
                        tradeData = {
                            'id': trade.attrib['id']
                        }
                        for details in trade.getchildren():
                            tradeData[details.tag] = details.text
                        trades.append(tradeData)
                # print(elem.tag + " => " + text)
                
        # print(trades) all trades made in bet
        if action == "place":
            PlaceBet(self.loginId, tradeid, totalamount)
        if action == "process":
            CreditUser(self.loginId, tradeid, totalamount)
            
        return (0, tradeid)

    def GetLoginResponse(self, status, requestAction, requestMessageId, user, token=None, client_ip=False):
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + user.pk + "</userid>"
            responseXml += "<username>" + self.loginId + "</username>"
            responseXml += "<acode></acode>"  # affiliate code (?)
            responseXml += "<currencyid>" + self.currencyId + "</currencyid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<sessiontoken>" + str(token) + "</sessiontoken>"
            if client_ip:
                responseXml += "<clientip>" + self.clientIp + "</clientip>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        else:
            return PackExceptionMessage(status, requestAction, requestMessageId) # not implemented yet
        return responseXml

    def GetBalanceResponse(self, status, requestAction, requestMessageId, user):
        # print("user balance: ")
        # print(user.main_wallet)
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<balance>" + str(user.main_wallet) + "</balance>"
            responseXml += "<currencyid>" + self.currencyId + "</currencyid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<timestamp>" + datetime.utcnow().strftime( "%Y-%m-%dT%I:%M:%S") + "</timestamp>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        else:
            return PackExceptionMessage(status, requestAction, requestMessageId)
        return responseXml
    
    def GetTradeResponse(self, status, requestAction, requestMessageId, tradeId):
        user = CustomUser.objects.get(username=self.loginId)
        currencyId = const.CURRENCY_MAP[user.currency]
        print("User placing trade: " + str(user))
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<currencyid>" + currencyId + "</currencyid>"
            responseXml += "<balance>" + str(user.main_wallet) + "</balance>"
            responseXml += "<tradeid>" + str(tradeId) + "</tradeid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<timestamp>" + datetime.utcnow().strftime( "%Y-%m-%dT%I:%M:%S") + "</timestamp>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        else:
            return PackExceptionMessage(status, requestAction, requestMessageId)
        return responseXml
    

def CreditUser(userid, tradeid, totalamount):
    user = CustomUser.objects.get(username=userid)
    logger.info("crediting amount: " + totalamount + " for winnings trade in trade: " + tradeid + " for user: " + str(user))
    new_balance = user.main_wallet + decimal.Decimal(totalamount)
    logger.info("user's balance is now: " + str(new_balance))
    user.main_wallet = new_balance
    return user.save()

def PlaceBet(userid, tradeid, totalamount):
    user = CustomUser.objects.get(username=userid)
    logger.info("processing " + tradeid + " for user: " + str(user))
    new_balance = user.main_wallet - decimal.Decimal(totalamount)
    user.main_wallet = new_balance
    return user.save()

def PackExceptionMessage(status, action, messageId):
    desc = DESC_MAP[status]
    exceptionMsg = '<?xml version="1.0" encoding="utf-16"?>'
    exceptionMsg += '<n2xsd:n2root xmlns:n2xsd="urn:n2ns" source="' + action + '">'
    exceptionMsg += '<status>' + str(status) + '</status>'
    exceptionMsg += '<exception action="' + action + '" id="' + messageId + '">'
    exceptionMsg += '<desc>' + desc + '</desc>'
    exceptionMsg += '</exception>'
    exceptionMsg += '</n2xsd:n2root>'
    return exceptionMsg

def ProcessTradeResult(self, xmlDoc):
    trades = [] # array of trade objects
    for root in xmlDoc.getchildren():
        for elem in root.getchildren():
            if not elem.text:
                text = "None"
            else:
                text = elem.text
            if elem.tag == "userid":
                self.loginId = text
            if elem.tag == "vendorid":
                self.vendorId = text
            if elem.tag == "totalamount":
                totalamount = text
            # if elem.tag == "gameid": record this data in bet history
            #     gameid = text
            if elem.tag == "tradeid":
                tradeid = text
            if elem.tag == 'trades':
                for trade in elem.getchildren():
                    tradeData = {
                        'id': trade.attrib['id']
                    }
                    for details in trade.getchildren():
                        tradeData[details.tag] = details.text
                    trades.append(tradeData)
    # print(trades)
    CreditUser(loginId, totalamount)
    # RecordBetOutcomes(trades) # function that records all the bets to user's bet history
    return (0, tradeId)