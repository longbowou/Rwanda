import channels_graphql_ws
import graphene

from rwanda.graphql.types import AccountType
from rwanda.user.models import User, Account


class OnlineSubscription(channels_graphql_ws.Subscription):
    name = "online-{}"
    account = graphene.Field(AccountType)

    class Arguments:
        auth_token = graphene.String(required=True)

    @staticmethod
    def subscribe(root, info, auth_token):
        user: User = info.context.user
        user.is_online = True
        user.save()

        AccountOnlineSubscription.broadcast(group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))

        return [OnlineSubscription.name.format(user.account.id.urn[9:])]

    @staticmethod
    def publish(payload, info, auth_token):
        return OnlineSubscription(account=info.context.user.account)

    @staticmethod
    def unsubscribed(root, info, auth_token):
        user: User = info.context.user
        user.disconnect()

        AccountOnlineSubscription.broadcast(group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))


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
