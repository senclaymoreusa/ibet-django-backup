from ftplib import FTP
from io import StringIO
from utils.constants import * 
from time import sleep
import logging
import datetime

logger = logging.getLogger('django')


class EaFTP():
    def __init__(self):
        i = 0
        while i < 3:
            try:
                logger.info('start connect to EA FTP server...')
                self.ftp_session = FTP()
                self.ftp_session.connect(EA_FTP_ADDR) 
                self.ftp_session.login(EA_FTP_USERNAME, EA_FTP_PASSWORD)
                break
            except Exception as e:
                logger.warning("(FATAL__ERROR) Connecting EA FTP error {}".format(str(e)))
                sleep(3)
                i += 1

class AgFTP():
    def __init__(self):
        for x in range(3):
            try:
                logger.info('start connect to AG FTP server...')
                self.ftp_session = FTP()
                self.ftp_session.connect(AG_FTP)
                self.ftp_session.login(AG_FTP_USERNAME, AG_FTP_PASSWORD)
                break
            except Exception as e:
                logger.warning("(FATAL__ERROR) Connecting AG FTP error {}".format(str(e)))
                sleep(3)
       

# def ftpConnect():
#     current_time = datetime.datetime.now().timestamp()
#     if EaFTP._instance is None or current_time - EaFTP.last_connection_time > 3600:      # refresh the connection
#         EaFTP._instance = EaFTP()
#         EaFTP.last_connection_time = current_time
#     return EaFTP._instance

# def agFtpConnect():
#     current_time = datetime.datetime.now().timestamp()
#     if AgFTP._instance is None or current_time - AgFTP.last_connection_time > 3600:      # refresh the connection
#         AgFTP._instance = AgFTP()
#         AgFTP.last_connection_time = current_time
#     return AgFTP._instance