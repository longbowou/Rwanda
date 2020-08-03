import graphene
from graphene_django_extras import DjangoFilterListField

from rwanda.graphql.account.mutations import AccountMutations
from rwanda.graphql.account.queries import AccountQueries
from rwanda.graphql.admin.mutations import AdminMutations
from rwanda.graphql.admin.queries import AdminQueries
from rwanda.graphql.purchase.mutations import PurchaseMutations
from rwanda.graphql.service.mutations import ServiceMutations
from rwanda.graphql.types import ServiceCategoryType, ServiceType


class Query(AccountQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    services = DjangoFilterListField(ServiceType)


class Mutation(AdminMutations, AccountMutations, ServiceMutations, PurchaseMutations):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)


class AdminQuery(AdminQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    services = DjangoFilterListField(ServiceType)


class AdminMutation(AdminMutations):
    pass


admin_schema = graphene.Schema(query=AdminQuery, mutation=AdminMutation)
