from datetime import datetime, timedelta

import graphene
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import date as date_filter

from rwanda.administration.models import Parameter
from rwanda.graphql.decorators import account_required
from rwanda.graphql.types import ServiceOrderType
from rwanda.service.models import Service, ServiceOption


class ServiceQueries(graphene.ObjectType):
    service_order_preview = graphene.Field(ServiceOrderType, service=graphene.UUID(required=True),
                                           service_options=graphene.List(graphene.NonNull(graphene.UUID)))

    @account_required
    def resolve_service_order_preview(self, info, service, service_options):
        service = Service.objects.get(pk=service)
        service_options = ServiceOption.objects.filter(id__in=service_options, service=service)

        base_price = int(Parameter.objects.get(label=Parameter.BASE_PRICE).value)
        commission = int(Parameter.objects.get(label=Parameter.COMMISSION).value)

        total_price = base_price
        total_delay = service.delay
        for service_option in service_options:
            total_delay += service_option.delay
            total_price += service_option.price

        must_be_delivered_at = datetime.today() + timedelta(days=total_delay)

        total_order_price = total_price + commission
        total_order_price_ttc = total_order_price

        total_order_price = intcomma(total_order_price)
        total_order_price_ttc = intcomma(total_order_price_ttc)
        cannot_pay_with_wallet = info.context.user.account.balance < total_price
        base_price = intcomma(base_price)
        commission = intcomma(commission)
        commission_tva = intcomma(0)
        total_price = intcomma(total_price)
        total_price_tva = intcomma(0)
        must_be_delivered_at = date_filter(must_be_delivered_at)

        return ServiceOrderType(
            total_order_price=total_order_price,
            total_order_price_ttc=total_order_price_ttc,
            cannot_pay_with_wallet=cannot_pay_with_wallet,
            base_price=base_price,
            commission=commission,
            commission_tva=commission_tva,
            total_price=total_price,
            total_price_tva=total_price_tva,
            must_be_delivered_at=must_be_delivered_at,
            total_delay=str(total_delay),
            service=service,
            serviceOptions=service_options,
        )
