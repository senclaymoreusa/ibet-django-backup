#https://stackoverflow.com/questions/51151271/can-i-compile-a-dll-project-to-a-shared-object-so-file-for-arm
#https://www.programiz.com/python-programming/methods/built-in/bytes
#https://instructobit.com/tutorial/101/Reconnect-a-Python-socket-after-it-has-lost-its-connection
#https://cs.lmu.edu/~ray/notes/pythonnetexamples/
#https://realpython.com/python-sockets/#socket-api-overview
#https://github.com/realpython/materials/tree/master/python-sockets-tutorial
#https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_eventdriven_programming.htm
#https://emptypage.jp/notes/pyevent.en.html
#https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
#https://realpython.com/intro-to-python-threading/

import sys
import socket
import selectors
import games.n2_socket.MessageHandler as MessageHandler
import sys, traceback
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import datetime


class ClientConnection:
    connected = False
    serverIP = ""
    serverPort = 0
    vendorId = 0
    passcode = ""
    threadId = 0
    selector = selectors.DefaultSelector()
    messageHandler = None
    sock = None

    #executor=None
    #event=None
    #pipeline=None
    #eventLock = None

    def __init__(self, SwamServerIP, SwamServerPort, VendorId, Passcode,
                 ThreadId):
        self.connected = True
        self.serverIP = SwamServerIP
        self.serverPort = SwamServerPort
        self.vendorId = VendorId
        self.passcode = Passcode
        self.messageHandler = MessageHandler.MessageHandler(
            self, VendorId, Passcode)
        self.sock = None
        self.threadId = ThreadId
        '''
        self.eventLock = threading.Lock()
        self.pipeline = queue.Queue()
        self.event = threading.Event() #The state is initially false.
        self.executor = ThreadPoolExecutor(10)
        future = self.executor.submit(self.ResponseMessageTask, self.pipeline, self.event)
        '''
    def Connect(self):
        try:
            print('Connecting to ' + self.serverIP + ' on port no ' +
                  str(self.serverPort) + '.....')
            #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self.connected = False
            self.sock = None
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.serverIP, self.serverPort))
            try:
                print('Connected to ' + self.serverIP + ' on port no ' +
                      str(self.serverPort))
                loginStr = 'login: ' + str(self.vendorId)
                print(loginStr)
                self.sock.sendall(bytes(loginStr, 'utf-8'))
                self.sock.setblocking(1)
                #ClientConnection.sock.settimeout(10)
                events = selectors.EVENT_READ | selectors.EVENT_WRITE
                self.selector.register(self.sock, events, data=None)
                self.connected = True
                while True:
                    events = self.selector.select(timeout=None)
                    # print("[" + str(datetime.datetime.now()) + "] EVENT!")
                    # print(events)
                    for key, mask in events:
                        self.ServiceNetworkEvent(key, mask)
                #except socket.error:
            except Exception as ex:
                self.CleanUp()
                print('Disconnect to ' + self.serverIP + ' on port no ' +
                      str(self.serverPort))
                print('Connect::Exception occurred', str(ex))
        except Exception as ex:
            print('Unable to connect to ' + self.serverIP + ' on port no ' +
                  str(self.serverPort))
            print('Connect::Exception occurred', str(ex))
            traceback.print_exc(file=sys.stdout)

    def ServiceNetworkEvent(self, key, mask):
        sock = key.fileobj
        data = key.data
        # print(sock, data)
        if mask & selectors.EVENT_READ:  # 1 --> client receiving msg from server
            encryptedString = self.GetNetworkData(self.sock)
            if encryptedString != None:
                message = self.DecryptPacket(encryptedString)
                if message != None:
                    responseMessage = self.messageHandler.ProcessRequestMessage(
                        message)
                    if responseMessage != None:
                        print("response message: " + str(responseMessage))
                        self.ProcessResponseMessage(sock, responseMessage)
            else:
                self.CleanUp()

    def GetNetworkData(self, sock):
        try:
            while True:
                networkByte = sock.recv(1)
                if networkByte != None:
                    if ord(networkByte) == 1:  #SOH
                        break
                else:
                    return None

            # print('SOH received, message incoming...')

            # get the data packet size
            networkByte = b''
            pos = 0
            while (pos < 5):
                byteData = sock.recv(1)
                # print(byteData)
                if byteData != None:
                    networkByte += byteData
                    pos = pos + 1
            # print("networkByte=" + str(networkByte))
            # networkByte = ClientConnection.GetBytes(networkByte, 5)
            packetSize = int(
                networkByte
            ) - 6  # remaining data size after minus SOH (1 byte) and length of packet (5 bytes)
            # print('packetSize=' + str(packetSize))
            # get the rest of network packet (including the EOT)
            networkByte = b''
            pos = 0
            while (pos < packetSize):
                byteData = sock.recv(packetSize - pos)
                if byteData != None:
                    networkByte += byteData
                    byteRead = len(byteData)
                    pos += byteRead
                else:
                    return None

            if ord(networkByte[-1:]) == 4:  #EOT
                # print('EOT reached')
                return networkByte[:-1]
            else:
                print('No EOT')
                return None
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
            return None
    def sumOfAscii(self, msg):
        return sum([ord(i) for i in msg])

    def ProcessResponseMessage(self, sock, responseMessage):
        try:
            print("Thread " + str(self.threadId) + " received this: " +
                  responseMessage)
            responseLen = len(responseMessage)
            totalAscii = self.sumOfAscii(responseMessage)

            checkSum = 256 - (totalAscii % 256)
            print("checksum: " + str(checkSum))
            responseMessage = self.GetBytes(bytes(responseMessage, 'utf-8'),
                                            responseLen)
            encryptedPacket = self.Endecrypt(self.passcode, len(self.passcode),
                                             responseMessage, responseLen)
            self.SendResponseMessage(sock, checkSum, encryptedPacket,
                                     responseLen)
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)

    def SendResponseMessage(self, sock, checkSum, encryptedPacket,
                            packetLength):
        try:
            networkBytes = bytearray()
            networkBytes.append(1)  #SOH
            packetSize = packetLength + 8
            #print(packetSize)
            packetSize = str(packetSize).zfill(5)
            #print(packetSize)
            # "packetsize=" . $packetSize . " checksum=" . chr($checkSum) EOT
            for x in range(5):
                networkBytes.append(ord(packetSize[x]))

            for x in range(packetLength):
                networkBytes.append(ord(encryptedPacket[x]))

            networkBytes.append(checkSum)
            networkBytes.append(4)

            # print(repr(networkBytes))
            #print(len(networkBytes))
            print("Sending Response")
            sock.sendall(networkBytes)
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)

    def DecryptPacket(self, encryptedPacket):
        try:
            #print('Received:', encryptedPacket)
            checkSum = ord(encryptedPacket[-1:])
            #print('checksum:', checkSum)
            sizeByte = len(encryptedPacket)
            encryptedPacket = encryptedPacket[:-1]  #remove checksum

            packetSize = len(encryptedPacket)
            encryptedPacket = self.GetBytes(encryptedPacket, packetSize)
            #print('GetBytes:', encryptedPacket)
            decryptedPacket = self.Endecrypt(self.passcode, len(self.passcode),
                                             encryptedPacket, packetSize)
            totalAscii = self.calculateTotalAsciiValue(decryptedPacket,
                                                       packetSize)
            if (checkSum + totalAscii) % 256 == 0:
                return decryptedPacket
            else:
                return None
            #print('Plain text:', decryptedPacket)
            #encryptedPacket="Jonathan Chong testing on encyption and decryption function"
            #print('Before:', encryptedPacket)
            #encryptedPacket = self.Decrypt(self.passcode,len(self.passcode),encryptedPacket,len(encryptedPacket))
            #print('After:', encryptedPacket)
            #decryptedPacket = self.Decrypt(self.passcode,len(self.passcode),encryptedPacket,len(encryptedPacket))
            #print('Original:', decryptedPacket)
            #return decryptedPacket
        except Exception as ex:
            #print('DecryptPacket::Exception occurred', str(ex))
            traceback.print_exc(file=sys.stdout)
            return None

    def Endecrypt(self, key, keyLen, packet, packetLen):
        output = ""
        for i in range(packetLen):
            output += chr(ord(packet[i]) ^ ord(key[i % keyLen]))
        return output

    def GetBytes(self, data, dataSize):
        dataBytes = ""
        for x in range(dataSize):
            dataBytes += chr(data[x])
        return dataBytes

    def calculateTotalAsciiValue(self, package, packetLen):
        totalAsciiValue = 0
        for x in range(packetLen):
            totalAsciiValue += ord(package[x])
        return totalAsciiValue

    def SendResponse(self, sock, responseMessage):
        print("server will receive this: " + responseMessage)
        #sock.sendall(bytes(responseMessage, 'utf-8'))

    def CleanUp(self):
        print("Cleaning up")
        if self.sock != None:
            if self.connected:
                self.selector.unregister(self.sock)
            self.sock.close()
        self.sock = None
        self.connected = False

    '''
    def AddResponseMessageQueue(self,responseMessage):
        try:
            self.pipeline.put(responseMessage)
            self.eventLock.acquire()
            self.event.set()
            self.eventLock.release()
        except Exception as ex:
            self.event.set()
            traceback.print_exc(file=sys.stdout)          
        
    def ResponseMessageTask(self,queue, event):
        try:
            while True:
                if event.wait():
                    if not queue.empty():
                        message = queue.get()
                        #print (message)
                        self.ProcessResponseMessage(self.sock,message)
                        self.eventLock.acquire()
                        event.clear()
                        self.eventLock.release()
                #else:
                #    event.clear()
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
    '''
