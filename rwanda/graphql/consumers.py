import channels_graphql_ws
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from graphql_jwt.shortcuts import get_user_by_token

from rwanda.graphql.account.subscriptions import AccountOnlineSubscription
from rwanda.graphql.schemas.account import schema


def auth_middleware(next_middleware, root, info, *args, **kwds):
    if kwds.__contains__("auth_token"):
        user = get_user_by_token(kwds['auth_token'])
        info.context.user = user
    return next_middleware(root, info, *args, **kwds)


class AccountGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    schema = schema
    middleware = [auth_middleware]

    async def on_connect(self, payload):
        pass

    async def disconnect(self, code):
        await super().disconnect(code)

        if self.scope.__contains__("user") and \
                self.scope['user'] is not None and \
                self.scope['user'] is not AnonymousUser:
            await disconnect_user(self.scope['user'])

            await AccountOnlineSubscription.broadcast_async(
                group=AccountOnlineSubscription.name.format(self.scope['user'].account.id.urn[9:]))


@database_sync_to_async
def disconnect_user(user):
    user.disconnect()
