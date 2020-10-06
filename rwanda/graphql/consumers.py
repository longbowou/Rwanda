import channels_graphql_ws
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from rwanda.graphql.account.subscriptions import AccountOnlineSubscription
from rwanda.graphql.schemas.account import schema


class AccountGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    schema = schema

    async def on_connect(self, payload):
        pass

    async def disconnect(self, code):
        await super().disconnect(code)

        if self.scope.__contains__("user") and \
                self.scope['user'] is not None and \
                not isinstance(self.scope['user'], AnonymousUser):
            await disconnect_user(self.scope['user'])

            await notify_on_disconnect(self.scope['user'])


@sync_to_async
def notify_on_disconnect(user):
    AccountOnlineSubscription.broadcast(
        group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))


@database_sync_to_async
def disconnect_user(user):
    user.disconnect()
