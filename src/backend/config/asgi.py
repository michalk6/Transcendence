"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
import config.routing

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": URLRouter(
        config.routing.websocket_urlpatterns
    ),
})
