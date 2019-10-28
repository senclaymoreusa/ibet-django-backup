#https://python101.pythonlibrary.org/chapter31_lxml.html
#https://medium.com/vaidikkapoor/understanding-non-blocking-i-o-with-python-part-1-ec31a2e2db9b

from concurrent.futures import ThreadPoolExecutor
from lxml import etree
import games.n2_socket.PlayerManagement as playerManagement
import logging

logger = logging.getLogger("django")

class MessageHandler:
    '''
    This class handles the delegation of the XML message action to its respective API call
    '''
    vendorId = 0
    passcode = ""
    executor = None
    connection = None

    def __init__(self, ClientConnection, VendorId, Passcode):
        self.vendorId = VendorId
        self.passcode = Passcode
        self.executor = ThreadPoolExecutor(5)
        self.connection = ClientConnection

    def ProcessRequestMessage(self, swamMessage):
        # print('Full message:\n', swamMessage)
        future = self.executor.submit(self.MessageTask, (swamMessage))
        return future.result(5)

    def MessageTask(self, swamXml):
        swamResponse = None
        try:
            xmlDoc = etree.fromstring(bytes(swamXml, 'utf-16'))
            
            elem = xmlDoc.getchildren()[0]
            messageAction = elem.attrib['action']
            messageId = elem.attrib['id']

            logger.info("Action: " + messageAction + ", id: " + messageId)

            if messageAction == 'spingalive':  #return nothing
                return None
            else:
                swamResponse = ''
                request = playerManagement.PlayerManagement(self.vendorId, self.passcode)
                if  messageAction == 'slogin':        
                    (retStatus, user) = request.ProcessLoginRequest(xmlDoc)
                    swamResponse = request.GetLoginResponse(retStatus, messageAction, messageId, user)
                if messageAction == 'swebsinglelogin':
                    (retStatus, user, token) = request.ProcessWebLoginRequest(xmlDoc)
                    swamResponse = request.GetLoginResponse(retStatus, messageAction, messageId, user, token, True)
                if messageAction == 'sgetbalance':
                    (retStatus, user) = request.ProcessGetBalance(xmlDoc)
                    swamResponse = request.GetBalanceResponse(retStatus, messageAction, messageId, user)
                if messageAction == 'splacetrade':
                    (retStatus, tradeId) = request.ProcessTradeRequest(xmlDoc, "place")
                    swamResponse = request.GetTradeResponse(retStatus, messageAction, messageId, tradeId)
                if messageAction == 'spushtrade':
                    (retStatus, tradeId) = request.ProcessTradeRequest(xmlDoc, "push")
                    swamResponse = request.GetTradeResponse(retStatus, messageAction, messageId, tradeId)
                if messageAction == 'straderesult':
                    (retStatus, tradeId) = request.ProcessTradeRequest(xmlDoc, "process")
                    swamResponse = request.GetTradeResponse(retStatus, messageAction, messageId, tradeId)

                #self.connection.AddResponseMessageQueue(swamResponse)
                return swamResponse

        except Exception as ex:
            logger.error('MessageTask::Action was "' + messageAction + '"\nException occurred' + repr(ex))
            # print('MessageTask::Action was "',messageAction,'"\nException occurred', repr(ex))
    