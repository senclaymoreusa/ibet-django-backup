from ftplib import FTP
from io import StringIO
from utils.constants import * 
import logging

logger = logging.getLogger('django')


class EaFTP():
    _instance = None

    def __init__(self):
        logger.info('start connect to EA FTP server...')
        self.ftp_session = FTP()
        self.ftp_session.connect(EA_FTP_ADDR) 
        self.ftp_session.login(EA_FTP_USERNAME, EA_FTP_PASSWORD)

class AgFTP():
    _instance = None

    def __init__(self):
        logger.info('start connect to EA FTP server...')
        self.ftp_session = FTP()
        # self.ftp_session.connect(EA_FTP_ADDR) 
        # self.ftp_session.login(EA_FTP_USERNAME, EA_FTP_PASSWORD)

def ftpConnect():
    if EaFTP._instance is None:
        EaFTP._instance = EaFTP()
    return EaFTP._instance