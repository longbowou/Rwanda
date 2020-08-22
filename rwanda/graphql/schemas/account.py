import graphene
import graphql_jwt
from graphene_django_extras import DjangoFilterListField

from rwanda.graphql.account.mutations import AccountMutations
from rwanda.graphql.account.queries import AccountQueries
from rwanda.graphql.admin.mutations import AdminMutations
from rwanda.graphql.purchase.mutations import PurchaseMutations
from rwanda.graphql.service.mutations import ServiceMutations
from rwanda.graphql.types import ServiceCategoryType, ServiceType, AccountType, LitigationType, AdminType, \
    ServicePurchaseType


class Query(AccountQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    admins = DjangoFilterListField(AdminType)
    service_purchases = DjangoFilterListField(ServicePurchaseType)
    accounts = DjangoFilterListField(AccountType)
    services = DjangoFilterListField(ServiceType)
    litigation = DjangoFilterListField(LitigationType)


class Mutation(AccountMutations, AdminMutations, ServiceMutations, PurchaseMutations):
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
