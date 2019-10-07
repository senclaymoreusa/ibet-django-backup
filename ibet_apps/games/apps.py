from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GamesConfig(AppConfig):
    name = 'games'
    verbose_name = _('3rd Party Game System')

    def ready(self):
        print("Games Config Ready")
        import games.n2_socket.Main as mainSocket
        mainSocket.main()
