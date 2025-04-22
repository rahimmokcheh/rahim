from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Modification du pattern pour accepter les espaces et caractères spéciaux dans les noms de caméra
    re_path(r'ws/camera/(?P<cam_name>[^/]+)/$', consumers.FireShieldConsumer.as_asgi()),
]