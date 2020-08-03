import graphene
from graphene_django_extras import DjangoFilterListField

from rwanda.graphql.account.mutations import AccountMutations
from rwanda.graphql.account.queries import AccountQueries
from rwanda.graphql.admin.mutations import AdminMutations
from rwanda.graphql.types import ServiceCategoryType, ServiceType


class Query(AccountQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    services = DjangoFilterListField(ServiceType)


class Mutation(AdminMutations, AccountMutations):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
