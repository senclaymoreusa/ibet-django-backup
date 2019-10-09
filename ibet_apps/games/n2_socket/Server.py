import socket
import datetime
from time import sleep

KEY = 'A92C2DA78C72C50E64AE79A192E1459B'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 1234))
s.listen(5)

ex = '<?xml version="1.0" encoding="utf-16"?><n2xsd:n2root xmlns:n2xsd="urn:n2ns"><request action="slogin" id="00291023033745682821"><userid>29</userid><password>29</password><vendorid>3</vendorid></request></n2xsd:n2root>'
getbalancereq = '<?xml version="1.0" encoding="utf-16"?>'
getbalancereq = '<n2xsd:n2root xmlns:n2xsd="urn:n2ns">'
getbalancereq = '<request action="sgetbalance" id="19100822100093204504">'
getbalancereq = '<userid>ibttest01</userid>'
getbalancereq = '<vendorid>390</vendorid>'
getbalancereq = '<currencyid>1111</currencyid>'
getbalancereq = '<sessiontoken>dasdasdasdasdadasd</sessiontoken>'
getbalancereq = '<timestamp>2019-10-08T22:10:00.955</timestamp></request></n2xsd:n2root>'

exampleMsg = '<?xml version="1.0" encoding="utf-16"?>'
exampleMsg += '<n2xsd:n2root xmlns:n2xsd="urn:n2ns">'
exampleMsg += '<request action="slogin" id="00291023033745682821">'
exampleMsg += '<userid>29</userid>'
exampleMsg += '<password>29</password>'
exampleMsg += '<vendorid>3</vendorid>'
exampleMsg += '</request>'
exampleMsg += '</n2xsd:n2root>'


def sumOfAscii(msg):
    return sum([ord(i) for i in msg])


def sxor(msg, key):  # return encrypted XML msg
    # convert strings to a list of character pair tuples
    # go through each tuple, converting them to ASCII code (ord)
    # perform exclusive or on the ASCII code
    # then convert the result back to ASCII (chr)
    # merge the resulting array of characters as a string
    output = ''
    for i in range(len(msg)):
        res = chr(ord(msg[i]) ^ ord(key[i % len(key)]))
        # print(res)
        output += res
    return output


def checksum(msg):
    return 256 - (sumOfAscii(msg) % 256)


def findNumZeroes(num):
    comp = 1
    i = 0
    while comp < num:
        i = i + 1
        comp = 1 * (10**i)

    return 5 - i


while True:
    try:
        client, address = s.accept()
        print(f'client connected from {address}')
        print("Preparing to send packet...")
        sleep(3)
        print("[" + str(datetime.datetime.now()) + "] sending SOH Byte...")
        client.send(bytes([0x01]))  # SOH

        print("[" + str(datetime.datetime.now()) + "] sending MsgSize Bytes...")
        encryptedMsg = sxor(exampleMsg, KEY)

        msgSize = len(encryptedMsg) + 8

        z = findNumZeroes(msgSize)

        client.send(bytes(z * '0' + str(msgSize),
                          "utf-8"))  # MsgSize with leading 0's

        xmlMsg = bytes(encryptedMsg, "utf-8")

        chksum = bytes(bin(checksum(ex)), "utf-8")
        client.send(xmlMsg)
        sleep(3)
        print("XML sent, preparing checksum...")
        # client.send(chksum)
        cs = bytearray()
        cs.append(checksum(ex))
        client.send(cs)
        print("Checksum sent... preparing EOT")
        sleep(3)
        client.send(bytes([0x04]))  # EOT

        msg = client.recv(8)
        print(msg.decode('utf-8'))
    except KeyboardInterrupt:
        print("Closing connection")
        s.close()
        break
