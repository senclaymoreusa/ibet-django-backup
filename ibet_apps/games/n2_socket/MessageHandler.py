#https://python101.pythonlibrary.org/chapter31_lxml.html
#https://medium.com/vaidikkapoor/understanding-non-blocking-i-o-with-python-part-1-ec31a2e2db9b

from concurrent.futures import ThreadPoolExecutor
from lxml import etree
import games.n2_socket.PlayerManagement as playerManagement


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
        print('Full message:', swamMessage)
        future = self.executor.submit(self.MessageTask, (swamMessage))
        return future.result(5)

    def MessageTask(self, swamXml):
        swamResponse = None
        try:
            xmlDoc = etree.fromstring(bytes(swamXml, 'utf-16'))
            
            for elem in xmlDoc.getchildren():
                messageAction = elem.attrib['action']
                messageId = elem.attrib['id']
                print(messageAction)
            if messageAction == 'spingalive':  #return nothing
                if int(messageId) % 100 == 0:
                    print(messageId)
            else:
                request = playerManagement.PlayerManagement(self.vendorId, self.passcode)
                if  messageAction == 'slogin':        
                    (retStatus, user) = request.ProcessLoginRequest(xmlDoc)
                    swamResponse = request.GetLoginResponse(retStatus, messageAction, messageId, user)
                    #self.connection.AddResponseMessageQueue(swamResponse)
                if messageAction == 'sgetbalance':
                    (retStatus, user) = request.ProcessGetBalance(xmlDoc)
                    swamResponse = request.GetBalanceResponse(retStatus, messageAction, messageId, user)
                    #self.connection.AddResponseMessageQueue(swamResponse)
                if messageAction == 'splacetrade':
                    print("place trade")
                    
                    swamResponse = request.GetTradeResponse(retStatus, messageAction, messageId, user)
                    
                if messageAction == '':
                    print("hi")
                return swamResponse

        except Exception as ex:
            print('MessageTask::Exception occurred', str(ex))
    

# if messageAction == 'swebsinglelogin':
#     print("hi")
#     loginRequest = playerManagement.PlayerManagement(
#         self.vendorId, self.passcode)
#     (retStatus, user) = loginRequest.ProcessLoginRequest(xmlDoc)