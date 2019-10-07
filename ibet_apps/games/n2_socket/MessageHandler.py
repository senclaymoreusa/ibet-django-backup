#https://python101.pythonlibrary.org/chapter31_lxml.html
#https://medium.com/vaidikkapoor/understanding-non-blocking-i-o-with-python-part-1-ec31a2e2db9b

from concurrent.futures import ThreadPoolExecutor
from lxml import etree
import games.n2_socket.PlayerManagement as playerManagement


class MessageHandler:
    vendorId = 0
    passcode = ""
    executor = None
    conenction = None

    def __init__(self, ClientConnection, VendorId, Passcode):
        self.vendorId = VendorId
        self.passcode = Passcode
        self.executor = ThreadPoolExecutor(5)
        self.conenction = ClientConnection

    def ProcessRequestMessage(self, swamMessage):
        future = self.executor.submit(self.MessageTask, (swamMessage))
        return future.result(5)

    def MessageTask(self, swamXml):
        swamResponse = None
        try:
            xmlDoc = etree.fromstring(bytes(swamXml, 'utf-16'))
            print(xmlDoc.getchildren())
            for elem in xmlDoc.getchildren():
                messageAction = elem.attrib['action']
                messageId = elem.attrib['id']
                print(messageAction)

            if messageAction == 'spingalive':  #return nothing
                if int(messageId) % 100 == 0:
                    print(messageId)
            elif messageAction == 'slogin':
                print("need to login")
                loginRequest = playerManagement.PlayerManagement(
                    self.vendorId, self.passcode)
                retStatus = loginRequest.ProcessLoginRequest(xmlDoc)
                swamResponse = loginRequest.GetLoginResponse(
                    retStatus, messageAction, messageId)
                #self.connection.AddResponseMessageQueue(swamResponse)
            elif messageAction == 'sgetbalance':
                #print(messageAction)
                balanceRequest = playerManagement.PlayerManagement(
                    self.vendorId, self.passcode)
                retStatus = balanceRequest.ProcessBalanceRequest(xmlDoc)
                swamResponse = balanceRequest.GetBalanceResponse(
                    retStatus, messageAction, messageId)
                #print("received this: " + swamMessage)
                #self.conenction.AddResponseMessageQueue(swamResponse)
            return swamResponse
        except Exception as ex:
            print('MessageTask::Exception occurred', str(ex))
