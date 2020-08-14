from datetime import datetime, timedelta

import graphene
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.administration.models import Parameter
from rwanda.graphql.mutations import DjangoModelMutation
from rwanda.graphql.purchase.operations import approve_service_purchase, cancel_service_purchase, init_service_purchase
from rwanda.graphql.types import ServicePurchaseType
from rwanda.purchase.models import ServicePurchase
from rwanda.service.models import Service, ServiceOption
from rwanda.user.models import Account


class InitServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("account", 'service', 'service_options')

    @classmethod
    def pre_mutate(cls, info, old_obj, form, input):
        price = int(Parameter.objects.get(label=Parameter.BASE_PRICE).value)
        service = Service.objects.get(pk=input.service)
        delay = service.delay

        if input.service_options is not None:
            for id in input.service_options:
                service_option = ServiceOption.objects.get(pk=id)
                price += service_option.price
                delay += service_option.delay

        if Account.objects.get(pk=input.account).balance < price:
            return cls(
                errors=[ErrorType(field="account", messages=[_("Insufficient amount to purchase service.")])])

        form.instance.price = price
        form.instance.delay = delay
        form.instance.commission = int(Parameter.objects.get(label=Parameter.COMMISSION).value)
        form.instance.must_be_delivered_at = datetime.today() + timedelta(days=delay)

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        init_service_purchase(obj)
        obj.refresh_from_db()


class AcceptServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.cannot_be_accepted:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])])

        service_purchase.set_as_accepted()


class DeliverServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.cannot_be_delivered:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])])

        service_purchase.set_as_delivered()


class ApproveServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.cannot_be_approved:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])])

        service_purchase.set_as_approved()

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        approve_service_purchase(obj)
        obj.refresh_from_db()


class CancelServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.cannot_be_canceled:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("You cannot canceled the purchase yet.")])])

        service_purchase.set_as_canceled()

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        cancel_service_purchase(obj)
        obj.refresh_from_db()


class PurchaseMutations(graphene.ObjectType):
    init_service_purchase = InitServicePurchase.Field()
    accept_service_purchase = AcceptServicePurchase.Field()
    approve_service_purchase = ApproveServicePurchase.Field()
    deliver_service_purchase = DeliverServicePurchase.Field()
    cancel_service_purchase = CancelServicePurchase.Field()
