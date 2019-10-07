from datetime import datetime


class PlayerManagement:
    loginId = None
    vendorId = None
    passcode = ''

    def __init__(self, VendorId, Passcode):
        self.loginId = ""
        self.vendorId = VendorId
        self.passcode = Passcode

    def ProcessLoginRequest(self, xmlDoc):
        retStatus = 0
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
        #ValidatePlayer()  # not implemented yet

        return retStatus

    def ProcessBalanceRequest(self, xmlDoc):
        retStatus = 0
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
                #print(elem.tag + " => " + text)

        #validate the user Id here
        #ValidatePlayer()  # not implemented yet

        return retStatus

    def GetLoginResponse(self, status, requestAction, requestMessageId):
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<username></username>"
            responseXml += "<acode></acode>"
            responseXml += "<currencyid>54</currencyid>"
            responseXml += "<balance>10000</balance>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<sessiontoken>dasdasdasdasdadasd</sessiontoken>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        #else
        #    PackExceptionMessage() # not implemented yet
        return responseXml

    def GetBalanceResponse(self, status, requestAction, requestMessageId):
        if status == 0:
            responseXml = "<?xml version=\"1.0\" encoding=\"utf-16\"?><n2xsd:n2root xmlns:n2xsd=\"urn:n2ns\">"
            responseXml += "<status>0</status>"
            responseXml += "<result action=\"" + requestAction + "\" id=\"" + requestMessageId + "\">"
            responseXml += "<userid>" + self.loginId + "</userid>"
            responseXml += "<balance>10000</balance>"
            responseXml += "<currencyid>54</currencyid>"
            responseXml += "<vendorid>" + self.vendorId + "</vendorid>"
            responseXml += "<merchantpasscode>" + self.passcode + "</merchantpasscode>"
            responseXml += "<timestamp>" + datetime.utcnow().strftime(
                "%Y-%m-%dT%I:%M:%S") + "</timestamp>"
            responseXml += "</result>"
            responseXml += "</n2xsd:n2root>"
        #else
        #    PackExceptionMessage() # not implemented yet
        return responseXml
