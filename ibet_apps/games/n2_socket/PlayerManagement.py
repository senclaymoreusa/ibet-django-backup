from datetime import datetime

from django.contrib.auth import authenticate
from users.models import CustomUser
from rest_framework.authtoken.models import Token

import decimal
import games.n2_socket.n2_constants as const


class PlayerManagement:
    loginId = None
    vendorId = None
    passcode = ''

    def __init__(self, VendorId, Passcode):
        self.loginId = ""
        self.vendorId = VendorId
        self.passcode = Passcode
        self.currencyId = ""

    def ValidatePlayer(self, login, pw, method):
        if method == "login":
            user = authenticate(username=login, password=pw)
            
            if user:
                print("user " + login + " exists")
                self.currencyId = const.CURRENCY_MAP[user.currency]
                return (0, user)
            else:
                print("user not found!")
                return (105, None)    
        else:
            user = CustomUser.objects.get(username=login)
            if user:
                try:
                    sessionToken = Token.objects.get(user_id=user)
                    return (0, user)
                except Exception as ex:
                    print("No session token for this user")
                    return (105, user)
            else:
                print("user not found!")
                return (105, None)

    def GetPlayerBalance(self, username, currencyId):
        user = CustomUser.objects.get(username=username)
        self.currencyId = currencyId
        if user:
            print("user " + username + " exists")
            return (0, user)
        else:
            print("user not found!")
            return (105, None)

    def ProcessLoginRequest(self, xmlDoc):
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

                print(elem.tag + " => " + text)
        
        #validate the user Id here
        return self.ValidatePlayer(self.loginId, playerPassword, "login") # returns tuple (status, user)

    def ProcessWebLoginRequest(self, xmlDoc):
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
                        session = text

                    print(elem.tag + " => " + text)
            
            #validate the user Id here
            return self.ValidatePlayer(self.loginId, sessionToken, "session") # returns tuple (status, user)

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
                
                print(elem.tag + " => " + text)
        
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
                # if elem.tag == "gameid": record this data 
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
                        # print(tradeData.tag + "=" + tradeData.text)
                
                print(elem.tag + " => " + text)
        print(trades)
        if action == "place":
            print(PlaceBet(self.loginId, tradeid, totalamount))
        if action == "process":
            print(CreditUser(self.loginId, tradeid, totalamount))
            
        return (0, tradeid)

    def GetLoginResponse(self, status, requestAction, requestMessageId, user):
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<username>" + str(user.first_name) + "</username>"
            responseXml += "<acode></acode>"  # affiliate code (not used?)
            responseXml += "<currencyid>" + self.currencyId + "</currencyid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<sessiontoken>dasdasdasdasdadasd</sessiontoken>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        else:
            return PackExceptionMessage(status, requestAction, requestMessageId) # not implemented yet
        return responseXml

    def GetBalanceResponse(self, status, requestAction, requestMessageId, user):
        print("user balance: ")
        print(user.main_wallet)
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
    print("crediting user " + totalamount + " for winnings trade in trade: " + tradeid + " for user: " + str(user))
    new_balance = user.main_wallet + decimal.Decimal(totalamount)
    print("user's balance is now: " + str(new_balance))
    user.main_wallet = new_balance
    return user.save()

def PlaceBet(userid, tradeid, totalamount):
    user = CustomUser.objects.get(username=userid)
    print("processing " + tradeid + " for user: " + str(user))
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
    print(trades)
    CreditUser(loginId, totalamount)
    # RecordBetOutcomes(trades) # TODO: function that records all the bets to user's bet history
    return (0, tradeId)