import graphene
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Q

from rwanda.account.models import RefundWay, Refund
from rwanda.administration.models import Parameter
from rwanda.graphql.decorators import admin_required
from rwanda.graphql.types import AdminType, RefundWayType, ParameterType, StatsType
from rwanda.purchase.models import Litigation, ServicePurchase
from rwanda.service.models import Service
from rwanda.user.models import Account


class AdminQueries(graphene.ObjectType):
    admin = graphene.Field(AdminType, required=True)
    refund_way = graphene.Field(RefundWayType, id=graphene.UUID(required=True))
    parameter = graphene.Field(ParameterType, id=graphene.UUID(required=True))
    stats = graphene.Field(StatsType)

    @admin_required
    def resolve_admin(root, info, **kwargs):
        return info.context.user.admin

    @admin_required
    def resolve_refund_way(root, info, id, **kwargs):
        return RefundWay.objects.get(pk=id)

    @admin_required
    def resolve_parameter(root, info, id, **kwargs):
        return Parameter.objects.get(pk=id)

    @admin_required
    def resolve_stats(root, info, **kwargs):
        return StatsType(
            services_count=intcomma(Service.objects.count()),
            services_accepted_count=intcomma(Service.objects.filter(status=Service.STATUS_ACCEPTED).count()),
            disputes_count=intcomma(Litigation.objects.count()),
            disputes_not_handled_count=intcomma(
                Litigation.objects.filter(~Q(status=Litigation.STATUS_HANDLED)).count()),
            refunds_count=intcomma(Refund.objects.count()),
            refunds_not_processed_count=intcomma(Refund.objects.filter(~Q(status=Refund.STATUS_PROCESSED)).count()),
            service_purchases_count=intcomma(ServicePurchase.objects.count()),
            service_purchases_not_approved_count=intcomma(
                ServicePurchase.objects.filter(~Q(status=ServicePurchase.STATUS_APPROVED)).count()),
            accounts_count=intcomma(Account.objects.count()),
        )
