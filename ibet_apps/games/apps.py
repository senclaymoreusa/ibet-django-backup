from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GamesConfig(AppConfig):
    name = 'games'
    verbose_name = _('3rd Party Game System')

    # def ready(self):
    #     import games.ftp.ftp_client as ftpClient

    #     print("Running FTP connection")
    #     r = ftpClient.ftpConnect()
    #     print("ftp ready")
