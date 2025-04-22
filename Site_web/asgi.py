import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from Superviseur import routing  # Remplacez par le nom de votre application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Site_web.settings')  # Remplacez par le nom de votre projet

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})