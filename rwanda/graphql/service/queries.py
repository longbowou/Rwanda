from datetime import datetime, timedelta

import graphene
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import date as date_filter

from rwanda.administration.utils import param_base_price, param_commission, param_home_max_page_size
from rwanda.graphql.decorators import account_required
from rwanda.graphql.types import ServiceOrderType, ServiceType, ServiceCategoryType
from rwanda.services.models import Service, ServiceOption, ServiceCategory


class ServiceQueries(graphene.ObjectType):
    services = graphene.List(ServiceType)
    service = graphene.Field(ServiceType, id=graphene.UUID(required=True))
    service_categories = graphene.List(ServiceCategoryType)
    service_category = graphene.Field(ServiceCategoryType, id=graphene.UUID(required=True))
    service_category_services = graphene.List(ServiceType, id=graphene.UUID(required=True))
    service_order_preview = graphene.Field(ServiceOrderType, service=graphene.UUID(required=True),
                                           service_options=graphene.List(graphene.NonNull(graphene.UUID)))

    def resolve_service_categories(self, info):
        return ServiceCategory.objects.order_by("index").filter(published=True)

    def resolve_service_category(self, info, id):
        return ServiceCategory.objects.get(pk=id)

    def resolve_service_category_services(self, info, id):
        return Service.objects.filter(
            service_category__id=id,
            published=True,
            published_by_admin=True,
            status=Service.STATUS_ACCEPTED).order_by("-accepted_at")

    def resolve_service(self, info, id):
        return Service.objects.get(pk=id)

    def resolve_services(self, info, *args, **kwargs):
        return Service.objects.filter(
            published=True,
            published_by_admin=True,
            status=Service.STATUS_ACCEPTED) \
                   .order_by("-accepted_at")[: param_home_max_page_size()]

    @account_required
    def resolve_service_order_preview(self, info, service, service_options):
        service = Service.objects.get(pk=service)
        service_options = ServiceOption.objects.filter(id__in=service_options, service=service)

        base_price = param_base_price()

        total_order_price = base_price
        total_delay = service.delay
        for service_option in service_options:
            total_delay += service_option.delay
            total_order_price += service_option.price

        total_order_price_ttc = total_order_price

        commission = total_order_price * param_commission()
        total_price = total_order_price - commission

        cannot_pay_with_wallet = info.context.user.account.balance < total_order_price

        deadline_at = datetime.today() + timedelta(days=total_delay)

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
            service_options=service_options,
        )
