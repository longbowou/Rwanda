import graphene
from django.contrib.humanize.templatetags.humanize import intcomma
from graphene_django_extras import DjangoFilterListField

from rwanda.administration.utils import param_currency, param_base_price
from rwanda.graphql.admin.mutations import AdminMutations
from rwanda.graphql.admin.queries import AdminQueries
from rwanda.graphql.decorators import admin_required
from rwanda.graphql.types import ServiceCategoryType, ServiceType, FundType, LitigationType, \
    ParametersType
from rwanda.purchase.models import Litigation


class AdminQuery(AdminQueries):
    service_categories = DjangoFilterListField(ServiceCategoryType)
    services = DjangoFilterListField(ServiceType)
    funds = DjangoFilterListField(FundType)
    parameters = graphene.Field(ParametersType, required=True)
    litigation = graphene.Field(LitigationType, required=True, id=graphene.UUID(required=True))

    @admin_required
    def resolve_litigation(self, info, id):
        return Litigation.objects.get(pk=id)

    @staticmethod
    def resolve_parameters(self, info):
        return ParametersType(currency=param_currency(),
                              base_price=intcomma(int(param_base_price())))


class AdminMutation(AdminMutations):
    pass


admin_schema = graphene.Schema(query=AdminQuery, mutation=AdminMutation)
