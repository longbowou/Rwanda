import channels_graphql_ws
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from graphql_jwt.shortcuts import get_user_by_token

from rwanda.graphql.account.subscriptions import AccountOnlineSubscription
from rwanda.graphql.schemas.account import schema


class AccountGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    schema = schema

    async def on_connect(self, payload):
        self.scope["is_authenticated"] = False

        if self.scope.__contains__("cookies") and self.scope['cookies'].__contains__("authToken"):
            user = await get_user(self.scope['cookies']['authToken'])
            if user is not None:
                self.scope["is_authenticated"] = True
                self.scope["user"] = user

    async def disconnect(self, code):
        await super().disconnect(code)

        if self.scope.__contains__("is_authenticated") and self.scope["is_authenticated"]:
            await disconnect_user(self.scope['user'])

            await notify_on_disconnect(self.scope['user'])


@database_sync_to_async
def get_user(auth_token):
    try:
        user = get_user_by_token(auth_token)
        return user
    except Exception:
        return None


@sync_to_async
def notify_on_disconnect(user):
    AccountOnlineSubscription.broadcast(
        group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))


@database_sync_to_async
def disconnect_user(user):
    user.disconnect()
