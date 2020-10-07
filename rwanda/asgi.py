"""
ASGI config for rwanda project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

import channels
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from django.urls import path

from rwanda.graphql.consumers import AccountGraphqlWsConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda.settings')

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        channels.routing.URLRouter([
            path('graphql-ws/', AccountGraphqlWsConsumer),
        ])
    )
})
