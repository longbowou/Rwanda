import channels_graphql_ws
import graphene
from graphql_jwt.shortcuts import get_user_by_token

from rwanda.graphql.types import AccountType
from rwanda.user.models import Account


class OnlineSubscription(channels_graphql_ws.Subscription):
    name = "online-{}"
    account = graphene.Field(AccountType)

    class Arguments:
        auth_token = graphene.String(required=True)

    @staticmethod
    def subscribe(root, info, auth_token):
        try:
            user = get_user_by_token(auth_token)
            user.is_online = True
            user.save()

            AccountOnlineSubscription.broadcast(group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))

            return [OnlineSubscription.name.format(user.account.id.urn[9:])]
        except Exception:
            pass

        return []

    @staticmethod
    def publish(payload, info, auth_token):
        try:
            user = get_user_by_token(auth_token)
            return OnlineSubscription(account=user.account)
        except Exception:
            pass

        return channels_graphql_ws.Subscription.SKIP

    @staticmethod
    def unsubscribed(root, info, auth_token):
        try:
            user = get_user_by_token(auth_token)
            user.disconnect()

            AccountOnlineSubscription.broadcast(group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))
        except Exception:
            pass


class AccountOnlineSubscription(channels_graphql_ws.Subscription):
    name = "account-online-{}"
    account = graphene.Field(AccountType)

    class Arguments:
        auth_token = graphene.String(required=True)
        account = graphene.UUID(required=True)

    @staticmethod
    def subscribe(root, info, auth_token, account):
        return [AccountOnlineSubscription.name.format(account.urn[9:])]

    @staticmethod
    def publish(payload, info, auth_token, account):
        return AccountOnlineSubscription(account=Account.objects.get(pk=account))


class AccountSubscriptions(graphene.ObjectType):
    online_subscription = OnlineSubscription.Field()
    account_online_subscription = AccountOnlineSubscription.Field()
