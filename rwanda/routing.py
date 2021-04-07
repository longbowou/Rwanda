import channels
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from django.urls import path

from rwanda.graphql.consumers import AccountGraphqlWsConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        channels.routing.URLRouter([
            path('graphql-ws/', AccountGraphqlWsConsumer.as_asgi()),
        ])
    )
})
