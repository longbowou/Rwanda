import graphene
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Q

from rwanda.account.models import RefundWay, Refund
from rwanda.accounting.models import Fund
from rwanda.administration.models import Parameter
from rwanda.administration.utils import param_currency
from rwanda.graphql.decorators import admin_required
from rwanda.graphql.types import AdminType, RefundWayType, ParameterType, StatsType, AccountType
from rwanda.purchase.models import Litigation, ServicePurchase
from rwanda.service.models import Service
from rwanda.user.models import Account, User


class AdminQueries(graphene.ObjectType):
    admin = graphene.Field(AdminType)
    stats = graphene.Field(StatsType)
    refund_way = graphene.Field(RefundWayType, id=graphene.UUID(required=True))
    parameter = graphene.Field(ParameterType, id=graphene.UUID(required=True))
    account = graphene.Field(AccountType, id=graphene.UUID(required=True))

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
        currency = param_currency()

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
            commissions_sum=intcomma(Fund.objects.get(label=Fund.COMMISSIONS).balance) + ' ' + currency,
        )

    @admin_required
    def resolve_account(root, info, id, **kwargs):
        return User.objects.get(pk=id).account
