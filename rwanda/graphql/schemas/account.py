import graphene
import graphql_jwt
from graphene_django_extras import DjangoFilterListField

from rwanda.administration.models import Parameter
from rwanda.graphql.account.mutations import AccountMutations
from rwanda.graphql.account.queries import AccountQueries
from rwanda.graphql.admin.mutations import AdminMutations
from rwanda.graphql.purchase.mutations import PurchaseMutations
from rwanda.graphql.service.mutations import ServiceMutations
from rwanda.graphql.types import ServiceCategoryType, ServiceType, LitigationType, ServicePurchaseType, ParametersType


class AccountQuery(AccountQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    service_purchases = DjangoFilterListField(ServicePurchaseType)
    services = DjangoFilterListField(ServiceType)
    litigation = DjangoFilterListField(LitigationType)
    parameters = graphene.Field(ParametersType)

    def resolve_parameters(root, info, **kwargs):
        return ParametersType(currency=Parameter.objects.get(label=Parameter.CURRENCY).value,
                              base_price=Parameter.objects.get(label=Parameter.BASE_PRICE).value)


class AccountMutation(AccountMutations, ServiceMutations, PurchaseMutations, AdminMutations):
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=AccountQuery, mutation=AccountMutation)
