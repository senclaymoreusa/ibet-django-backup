import games.n2_socket.MainService as mainService
import threading
import socket

# "192.168.2.53"
print("Connecting to N2 games...")

N2_IP = "121.127.21.181"
N2_PORT = 8081
N2_VENDORID = 390
N2_PASSCODE = "A92C2DA78C72C50E64AE79A192E1459B"


def main():
    try:
        print("Connecting to N2 games...")
        event = threading.Event()
        main = mainService.MainService("127.0.0.1", 1234, 390,
                                       "A92C2DA78C72C50E64AE79A192E1459B")
        # main = mainService.MainService(N2_IP, N2_PORT, 54,
        #                                "9F340A56DC334E1E9FB24AE2B0B4D7EE")
        main.Start(event)
    except Exception as ex:
        print('Start::Exception occurred', str(ex))


main()
