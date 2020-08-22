import graphene
import graphql_jwt
from graphene_django_extras import DjangoFilterListField

from rwanda.graphql.admin.mutations import AdminMutations
from rwanda.graphql.admin.queries import AdminQueries
from rwanda.graphql.types import ServiceCategoryType, ServiceType, FundType, ParameterType


class AdminQuery(AdminQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    services = DjangoFilterListField(ServiceType)
    funds = DjangoFilterListField(FundType)
    parameters = DjangoFilterListField(ParameterType)


class AdminMutation(AdminMutations):
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


admin_schema = graphene.Schema(query=AdminQuery, mutation=AdminMutation)
