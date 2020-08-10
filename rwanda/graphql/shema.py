import graphene
from graphene_django_extras import DjangoFilterListField

from rwanda.graphql.account.mutations import AccountMutations
from rwanda.graphql.account.queries import AccountQueries
from rwanda.graphql.purchase.mutations import PurchaseMutations
from rwanda.graphql.service.mutations import ServiceMutations
from rwanda.graphql.types import ServiceCategoryType, ServiceType, AccountType, LitigationType


class Query(AccountQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    accounts = DjangoFilterListField(AccountType)
    services = DjangoFilterListField(ServiceType)
    litigations = DjangoFilterListField(LitigationType)


class Mutation(AccountMutations, ServiceMutations, PurchaseMutations):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
