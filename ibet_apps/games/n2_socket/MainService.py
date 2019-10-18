#!/usr/bin/env python3
# Author: Jonathan Chong & Orion Ou
# This sample uses python 3.7.4 socket programming to connect to Swam Tcp Server
# What are in this sample:
#       1) Able to connect, receive (and decode data) and send (and encode) data from/to Swam Tcp Server
#       2) Able to reconnect to Swam Tcp Server in the event of disconnection
#       3) 2 client sockets were established to Swam Tcp Server
#       4) Able to detect CTRL-C for terminating the program
#

import logging
import games.n2_socket.ClientConnection as ClientConnection
#import ClientConnection2
import threading
from time import sleep


class MainService:
    swamServer = ""
    swamPort = 0
    vendorId = 0
    passcode = ""
    swamClientList = []

    def __init__(self, SwamServer, SwamPort, VendorId, Passcode):
        self.swamServer = SwamServer
        self.swamPort = SwamPort
        self.vendorId = VendorId
        self.passcode = Passcode

    def Start(self, event):
        try:
            for index in range(2):
                thread = threading.Thread(target=self.MakeConnectionThread,
                                          args=(index + 1, event), daemon=True)
                thread.start()
        except Exception as ex:
            print('Start::Exception occurred', str(ex))

    def MakeConnectionThread(self, threadId, event):
        print("Thread Id: ", threadId)
        swamClient = ClientConnection.ClientConnection(self.swamServer,
                                                       self.swamPort,
                                                       self.vendorId,
                                                       self.passcode, threadId)
        while True:
            swamClient.Connect()
            sleep(5)  #wait for 5 seconds before reconnect
        '''                                
                elif threadId == 2:
                        swamClient = ClientConnection2.ClientConnection2(self.swamServer,self.swamPort,self.vendorId,self.passcode)
                        while True:
                                swamClient.Connect()
                                sleep(5)
                '''
