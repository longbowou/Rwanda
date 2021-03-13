import channels_graphql_ws
import graphene

from rwanda.graphql.types import AccountType
from rwanda.users.models import User, Account


class OnlineSubscription(channels_graphql_ws.Subscription):
    name = "online-{}"
    account = graphene.Field(AccountType)

    @staticmethod
    def subscribe(root, info):
        if info.context.is_authenticated:
            user: User = info.context.user
            user.is_online = True
            user.save()

            AccountOnlineSubscription.broadcast(group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))

            return [OnlineSubscription.name.format(user.account.id.urn[9:])]
        return []

    @staticmethod
    def publish(payload, info):
        if info.context.is_authenticated:
            return OnlineSubscription(account=info.context.user.account)

        return channels_graphql_ws.Subscription.SKIP

    @staticmethod
    def unsubscribed(root, info):
        if info.context.is_authenticated:
            user: User = info.context.user
            user.disconnect()

            AccountOnlineSubscription.broadcast(group=AccountOnlineSubscription.name.format(user.account.id.urn[9:]))


class AccountOnlineSubscription(channels_graphql_ws.Subscription):
    name = "account-online-{}"
    account = graphene.Field(AccountType)

    class Arguments:
        account = graphene.UUID(required=True)

    @staticmethod
    def subscribe(root, info, account):
        return [AccountOnlineSubscription.name.format(account.urn[9:])]

    @staticmethod
    def publish(payload, info, account):
        if info.context.is_authenticated:
            return AccountOnlineSubscription(account=Account.objects.get(pk=account))

        return channels_graphql_ws.Subscription.SKIP


class AccountSubscriptions(graphene.ObjectType):
    online_subscription = OnlineSubscription.Field()
    account_online_subscription = AccountOnlineSubscription.Field()
