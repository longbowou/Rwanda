import graphene

from rwanda.graphql.decorators import account_required
from rwanda.graphql.types import AccountType


class AccountQueries(graphene.ObjectType):
    account = graphene.Field(AccountType, required=True)

    @account_required
    def resolve_account(root, info, **kwargs):
        return info.context.user.account
