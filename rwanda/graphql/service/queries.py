from datetime import datetime, timedelta

import graphene
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import date as date_filter
from graphene_django_extras import DjangoFilterListField

from rwanda.administration.utils import param_base_price, param_commission
from rwanda.graphql.decorators import account_required
from rwanda.graphql.types import ServiceOrderType, ServiceType
from rwanda.service.models import Service, ServiceOption


class ServiceQueries(graphene.ObjectType):
    services = DjangoFilterListField(ServiceType)
    service = graphene.Field(ServiceType, required=True, id=graphene.UUID(required=True))
    service_order_preview = graphene.Field(ServiceOrderType, required=True, service=graphene.UUID(required=True),
                                           service_options=graphene.List(graphene.NonNull(graphene.UUID)))

    def resolve_service(self, info, id):
        return Service.objects.get(pk=id)

    @account_required
    def resolve_service_order_preview(self, info, service, service_options):
        service = Service.objects.get(pk=service)
        service_options = ServiceOption.objects.filter(id__in=service_options, service=service)

        base_price = int(param_base_price())
        commission = int(param_commission())

        total_price = base_price
        total_delay = service.delay
        for service_option in service_options:
            total_delay += service_option.delay
            total_price += service_option.price

        deadline_at = datetime.today() + timedelta(days=total_delay)

        total_order_price = total_price + commission
        total_order_price_ttc = total_order_price

        cannot_pay_with_wallet = info.context.user.account.balance < total_order_price

        total_order_price = intcomma(total_order_price)
        total_order_price_ttc = intcomma(total_order_price_ttc)
        base_price = intcomma(base_price)
        commission = intcomma(commission)
        commission_tva = intcomma(0)
        total_price = intcomma(total_price)
        total_price_tva = intcomma(0)
        deadline_at = date_filter(deadline_at)

        return ServiceOrderType(
            total_order_price=total_order_price,
            total_order_price_ttc=total_order_price_ttc,
            cannot_pay_with_wallet=cannot_pay_with_wallet,
            base_price=base_price,
            commission=commission,
            commission_tva=commission_tva,
            total_price=total_price,
            total_price_tva=total_price_tva,
            deadline_at=deadline_at,
            total_delay=str(total_delay),
            service=service,
            serviceOptions=service_options,
        )
