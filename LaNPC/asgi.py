"""
ASGI config for LaNPC project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

import user.routing
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LaNPC.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Add WebSocket and other protocol routers here if needed
    'websocket' : AuthMiddlewareStack(
        URLRouter(
            user.routing.websocket_urlpatterns
        )
    )
})
