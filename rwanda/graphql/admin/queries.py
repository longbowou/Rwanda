import graphene

from rwanda.account.models import RefundWay
from rwanda.administration.models import Parameter
from rwanda.graphql.decorators import admin_required
from rwanda.graphql.types import AdminType, RefundWayType, ParameterType


class AdminQueries(graphene.ObjectType):
    admin = graphene.Field(AdminType, required=True)
    refund_way = graphene.Field(RefundWayType, id=graphene.UUID(required=True))
    parameter = graphene.Field(ParameterType, id=graphene.UUID(required=True))

    @admin_required
    def resolve_admin(root, info, **kwargs):
        return info.context.user.admin

    @admin_required
    def resolve_refund_way(root, info, id, **kwargs):
        return RefundWay.objects.get(pk=id)

    @admin_required
    def resolve_parameter(root, info, id, **kwargs):
        return Parameter.objects.get(pk=id)
