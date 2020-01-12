from ftplib import FTP
from io import StringIO
from utils.constants import * 
from time import sleep
import logging
import datetime

logger = logging.getLogger('django')


class EaFTP():
    _instance = None
    last_connection_time = None

    def __init__(self):
        i = 0
        while i <= 5:
            try:
                logger.info('start connect to EA FTP server...')
                self.ftp_session = FTP()
                self.ftp_session.connect(EA_FTP_ADDR) 
                self.ftp_session.login(EA_FTP_USERNAME, EA_FTP_PASSWORD)
                break
            except Exception as e:
                logger.critical("(FATAL__ERROR) Connecting EA FTP error", e)
                sleep(3)
                i += 1

class AgFTP():
    _instance = None

    def __init__(self):
        logger.info('start connect to EA FTP server...')
        self.ftp_session = FTP()
        # self.ftp_session.connect(EA_FTP_ADDR) 
        # self.ftp_session.login(EA_FTP_USERNAME, EA_FTP_PASSWORD)

def ftpConnect():
    current_time = datetime.datetime.now().timestamp()
    if EaFTP._instance is None or current_time - EaFTP.last_connection_time > 3600:      # refresh the connection
        EaFTP._instance = EaFTP()
        EaFTP.last_connection_time = current_time
    return EaFTP._instance