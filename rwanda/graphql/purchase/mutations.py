from datetime import datetime, timedelta

import graphene
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.accounting.models import Operation, Fund
from rwanda.administration.models import Parameter
from rwanda.graphql.mutations import DjangoModelMutation
from rwanda.graphql.types import ServicePurchaseType
from rwanda.purchase.models import ServicePurchase
from rwanda.service.models import Service, ServiceOption
from rwanda.user.models import Account


class InitServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("account", 'service', 'service_options')

    @classmethod
    def pre_mutate(cls, old_obj, form, input):
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
    def post_mutate(cls, old_obj, form, obj, input):
        Operation(type=Operation.DEBIT, account=obj.account, amount=obj.price,
                  fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
        Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') - obj.price)
        Account.objects.filter(pk=input.account).update(balance=F('balance') - obj.price)

        Operation(type=Operation.CREDIT, service_purchase=obj, amount=obj.fees,
                  fund=Fund.objects.get(label=Fund.MAIN)).save()
        Fund.objects.filter(label=Fund.MAIN).update(balance=F('balance') + obj.fees)

        Operation(type=Operation.CREDIT, service_purchase=obj, amount=obj.commission,
                  fund=Fund.objects.get(label=Fund.COMMISSIONS)).save()
        Fund.objects.filter(label=Fund.COMMISSIONS).update(balance=F('balance') + obj.commission)
        obj.refresh_from_db()


class AcceptServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.accepted or service_purchase.approved or service_purchase.delivered \
                or service_purchase.canceled:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])])

        service_purchase.accepted = True
        service_purchase.accepted_at = datetime.today()


class DeliverServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.delivered or service_purchase.approved or service_purchase.canceled:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])])

        if not service_purchase.accepted:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[
                    _("You cannot deliver the service for now. You must first accept the purchase.")])])

        service_purchase.delivered = True
        service_purchase.delivered_at = datetime.today()


class ApproveServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.approved or service_purchase.canceled:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])])

        if not service_purchase.accepted:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[
                    _("You cannot approved the purchase for now. The purchase must be accepted first.")])])

        if not service_purchase.delivered:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[
                    _("You cannot approved the purchase for now. The purchase must be delivered first.")])])

        service_purchase.approved = True
        service_purchase.approved_at = datetime.today()

    @classmethod
    def post_mutate(cls, old_obj, form, obj, input):
        Operation(type=Operation.DEBIT, service_purchase=obj, amount=obj.fees,
                  fund=Fund.objects.get(label=Fund.MAIN)).save()
        Fund.objects.filter(label=Fund.MAIN).update(balance=F('balance') - obj.fees)

        Operation(type=Operation.CREDIT, account=obj.service.account, amount=obj.fees,
                  fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
        Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') + obj.fees)
        Account.objects.filter(pk=obj.service.account.id).update(balance=F('balance') + obj.fees)
        obj.refresh_from_db()


class CancelServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_mutate(cls, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance
        if service_purchase.canceled or service_purchase.delivered or service_purchase.approved:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])])

        today = datetime.today()
        if service_purchase.accepted:
            timedelta = today - service_purchase.must_be_delivered_at

            if int(Parameter.objects.get(label=Parameter.DELAY_FOR_SERVICE_PURCHASE_CANCEL).value) < timedelta.days:
                return cls(
                    errors=[ErrorType(field="service_purchase", messages=[
                        _("You can not cancel purchase for now. But you can make a cancel request.")])])

        service_purchase.canceled = True
        service_purchase.canceled_at = today

    @classmethod
    def post_mutate(cls, old_obj, form, obj, input):
        Operation(type=Operation.DEBIT, service_purchase=obj, amount=obj.fees,
                  fund=Fund.objects.get(label=Fund.MAIN)).save()
        Fund.objects.filter(label=Fund.MAIN).update(balance=F('balance') - obj.fees)

        Operation(type=Operation.DEBIT, service_purchase=obj, amount=obj.commission,
                  fund=Fund.objects.get(label=Fund.COMMISSIONS)).save()
        Fund.objects.filter(label=Fund.COMMISSIONS).update(balance=F('balance') - obj.commission)

        Operation(type=Operation.CREDIT, account=obj.account, amount=obj.price,
                  fund=Fund.objects.get(label=Fund.ACCOUNTS)).save()
        Fund.objects.filter(label=Fund.ACCOUNTS).update(balance=F('balance') + obj.price)
        Account.objects.filter(pk=obj.account.id).update(balance=F('balance') + obj.price)
        obj.refresh_from_db()


class PurchaseMutations(graphene.ObjectType):
    init_service_purchase = InitServicePurchase.Field()
    accept_service_purchase = AcceptServicePurchase.Field()
    approve_service_purchase = ApproveServicePurchase.Field()
    deliver_service_purchase = DeliverServicePurchase.Field()
    cancel_service_purchase = CancelServicePurchase.Field()
