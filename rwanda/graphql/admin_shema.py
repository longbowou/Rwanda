import graphene
from graphene_django_extras import DjangoFilterListField

from rwanda.graphql.admin.mutations import AdminMutations
from rwanda.graphql.admin.queries import AdminQueries
from rwanda.graphql.types import ServiceCategoryType, ServiceType


class AdminQuery(AdminQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    services = DjangoFilterListField(ServiceType)


class AdminMutation(AdminMutations):
    pass


admin_schema = graphene.Schema(query=AdminQuery, mutation=AdminMutation)
