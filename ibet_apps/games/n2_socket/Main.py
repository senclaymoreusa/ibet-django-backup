import games.n2_socket.MainService as mainService
import threading
import socket
import boto3

import utils.aws_helper

print("Connecting to N2 games...")

AWS_S3_ADMIN_BUCKET = "ibet-admin-dev"
keys = utils.aws_helper.getThirdPartyKeys(AWS_S3_ADMIN_BUCKET, 'config/thirdPartyKeys.json')

N2_IP = keys["N2_GAMES"]["N2_IP"]
N2_PORT = keys["N2_GAMES"]["N2_PORT"]
N2_VENDORID = keys["N2_GAMES"]["N2_VENDORID"]
N2_PASSCODE = keys["N2_GAMES"]["N2_PASSCODE"]


def main():
    try:
        print("Connecting to N2 games...")
        event = threading.Event()
        main = mainService.MainService(N2_IP, N2_PORT, N2_VENDORID,
                                       N2_PASSCODE)
        main.Start(event)
    except Exception as ex:
        print('Start::Exception occurred', str(ex))


main()
