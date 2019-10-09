from datetime import datetime

from django.contrib.auth import authenticate
from users.models import CustomUser

import games.n2_socket.n2_constants


class PlayerManagement:
    loginId = None
    vendorId = None
    passcode = ''

    def __init__(self, VendorId, Passcode):
        self.loginId = ""
        self.vendorId = VendorId
        self.passcode = Passcode

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
        return ValidatePlayer(self.loginId, playerPassword) # returns tuple (user, status)
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
        
        #validate the user Id here
        return GetPlayerBalance(self.loginId, currencyId) # returns tuple (user, status)

    def ProcessTradeRequest(self, xmlDoc):
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

                print(elem.tag + " => " + text)
        
        return 0

    def GetLoginResponse(self, status, requestAction, requestMessageId, user):
        currencyId = CURRENCY_MAP[user.currency]
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<username>" + user.first_name + "</username>"
            responseXml += "<acode></acode>"
            responseXml += "<currencyid>" + currencyId + "</currencyid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<sessiontoken>dasdasdasdasdadasd</sessiontoken>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        else:
           PackExceptionMessage("slogin", status, requestAction, requestMessageId) # not implemented yet
        return responseXml

    def GetBalanceResponse(self, status, requestAction, requestMessageId, user):
        currencyId = CURRENCY_MAP[user.currency]
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<balance>" + str(user.main_wallet) + "</balance>"
            responseXml += "<currencyid>" + currencyId + "</currencyid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<timestamp>" + datetime.utcnow().strftime( "%Y-%m-%dT%I:%M:%S") + "</timestamp>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        else:
           PackExceptionMessage("slogin", status, requestAction, requestMessageId)
        return responseXml

def GetPlayerBalance(username, currencyId):
    pass


def ValidatePlayer(login, pw):
    user = authenticate(username=login, password=pw)
    if user:
        print("user " + login + "exists")
        return (0, user)
    else:
        print("user not found!")
        return (105, None)    

def PackExceptionMessage(source, status, action, messageId):
    desc = DESC_MAP[status]
    exceptionMsg = '<?xml version="1.0" encoding="utf-16"?>'
    exceptionMsg += '<n2xsd:n2root xmlns:n2xsd="urn:n2ns" source="' + source + '">'
    exceptionMsg += '<status>' + str(status) + '</status>'
    exceptionMsg += '<exception action="' + action + '" id="' + messageId + '">'
    exceptionMsg += '<desc>' + desc + '</desc>'
    exceptionMsg += '</exception>'
    exceptionMsg += '</n2xsd:n2root>'
    return exceptionMsg

