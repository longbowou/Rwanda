import graphene

from rwanda.account.models import RefundWay
from rwanda.graphql.decorators import account_required
from rwanda.graphql.types import AccountType, RefundWayType


class AccountQueries(graphene.ObjectType):
    account = graphene.Field(AccountType)
    refund_ways = graphene.List(RefundWayType)

    @account_required
    def resolve_account(root, info, **kwargs):
        return info.context.user.account

    @account_required
    def resolve_refund_ways(root, info, **kwargs):
        return RefundWay.objects.filter(published=True).all()
