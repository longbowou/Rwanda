import graphene
import graphql_jwt
from django.contrib.humanize.templatetags.humanize import intcomma

from rwanda.administration.utils import param_currency, param_base_price, param_deposit_fee
from rwanda.graphql.account.mutations import AccountMutations
from rwanda.graphql.account.queries import AccountQueries
from rwanda.graphql.account.subscriptions import AccountSubscriptions
from rwanda.graphql.decorators import account_required
from rwanda.graphql.purchase.mutations import PurchaseMutations
from rwanda.graphql.purchase.queries import PurchaseQueries
from rwanda.graphql.purchase.subscriptions import PurchaseSubscriptions
from rwanda.graphql.service.mutations import ServiceMutations
from rwanda.graphql.service.queries import ServiceQueries
from rwanda.graphql.types import ParametersType, PaymentType
from rwanda.payments.models import Payment


class AccountQuery(ServiceQueries, PurchaseQueries, AccountQueries):
    parameters = graphene.Field(ParametersType)
    payment = graphene.Field(PaymentType, id=graphene.UUID(required=True))

    @staticmethod
    def resolve_parameters(self, info):
        return ParametersType(currency=param_currency(),
                              base_price=intcomma(param_base_price()),
                              deposit_fee=param_deposit_fee())

    @account_required
    def resolve_payment(self, info, id):
        return Payment.objects.get(pk=id)


class AccountMutation(AccountMutations, ServiceMutations, PurchaseMutations):
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


class Subscription(PurchaseSubscriptions, AccountSubscriptions):
    pass


schema = graphene.Schema(query=AccountQuery, mutation=AccountMutation, subscription=Subscription)
