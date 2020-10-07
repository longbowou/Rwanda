import os

import channels
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from django.urls import path

from rwanda.graphql.consumers import AccountGraphqlWsConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda.settings')

django.setup()

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        channels.routing.URLRouter([
            path('graphql-ws/', AccountGraphqlWsConsumer),
        ])
    )
})
