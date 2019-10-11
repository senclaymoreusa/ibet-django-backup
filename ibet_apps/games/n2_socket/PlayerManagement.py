from datetime import datetime

from django.contrib.auth import authenticate
from users.models import CustomUser

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

    def ValidatePlayer(self, login, pw):
        user = authenticate(username=login, password=pw)
        if user:
            print("user " + login + " exists")
            self.currencyId = const.CURRENCY_MAP[user.currency]
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
        return self.ValidatePlayer(self.loginId, playerPassword) # returns tuple (status, user)
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
        return GetPlayerBalance(self.loginId, currencyId) # returns tuple (status, user)

    def ProcessTradeRequest(self, xmlDoc):
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
                if elem.tag == "password":
                    playerPassword = text
                if elem.tag == "gameid":
                    gameid = text
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


                # if elem.tag == "trade":
                #     tradeid = elem.attrib['id']
                # if elem.tag == "amount":
                #     print("bet this amount")
                #     amount = text
                
                print(elem.tag + " => " + text)
        print(trades)
        # MakeTrade(gameid, tradeid, amount) # to implement
        return [0, tradeid]

    def GetLoginResponse(self, status, requestAction, requestMessageId, user):
        print("Currency ID: " + self.currencyId)
        currencyId = self.currencyId
        print("Currency ID: " + currencyId) 
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<username>" + str(user.first_name) + "</username>"
            responseXml += "<acode></acode>"
            responseXml += "<currencyid>" + currencyId + "</currencyid>"
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
        print("User placing trade: " + str(user))
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<currencyid>" + self.currencyId + "</currencyid>"
            responseXml += "<balance>" + str(user.main_wallet) + "</balance>"
            responseXml += "<tradeid>" + str(tradeId) + "</tradeid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<timestamp>" + datetime.utcnow().strftime( "%Y-%m-%dT%I:%M:%S") + "</timestamp>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        else:
            return PackExceptionMessage(status, requestAction, requestMessageId)

    def PushTradeResponse(self):
        pass

def MakeTrade():
    pass

def GetPlayerBalance(username, currencyId):
    user = CustomUser.objects.get(username=username)
    if user:
        print("user " + username + " exists")
        return (0, user)
    else:
        print("user not found!")
        return (105, None)



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

