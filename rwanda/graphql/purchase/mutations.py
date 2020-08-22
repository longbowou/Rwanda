import graphene
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.administration.models import Parameter
from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation
from rwanda.graphql.purchase.operations import approve_service_purchase, cancel_service_purchase, init_service_purchase
from rwanda.graphql.types import ServicePurchaseType
from rwanda.purchase.models import ServicePurchase


class InitServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ('service', 'service_options')

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        price = int(Parameter.objects.get(label=Parameter.BASE_PRICE).value)
        service = form.cleaned_data.service
        delay = service.delay

        for service_option in form.cleaned_data.service_options:
            price += service_option.price
            delay += service_option.delay

        if info.context.user.account.balance < price:
            return cls(
                errors=[ErrorType(field="account", messages=[_("Insufficient amount to purchase service.")])])

        form.instance.price = price
        form.instance.delay = delay
        form.instance.commission = int(Parameter.objects.get(label=Parameter.COMMISSION).value)

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        init_service_purchase(obj)
        obj.refresh_from_db()


class AcceptServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.service.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_accepted:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("You cannot perform this action.")])],
                servicePurchase=service_purchase)

        service_purchase.set_as_accepted()


class DeliverServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.service.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_delivered:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("You cannot perform this action.")])],
                servicePurchase=service_purchase)

        service_purchase.set_as_delivered()


class ApproveServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_approved:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("Purchase already processed.")])],
                servicePurchase=service_purchase)

        service_purchase.set_as_approved()

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        approve_service_purchase(obj)
        obj.refresh_from_db()


class CancelServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_canceled:
            return cls(
                errors=[ErrorType(field="service_purchase", messages=[_("You cannot perform this action.")])],
                servicePurchase=service_purchase)

        service_purchase.set_as_canceled()

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        cancel_service_purchase(obj)
        obj.refresh_from_db()


class PurchaseMutations(graphene.ObjectType):
    init_service_purchase = InitServicePurchase.Field()
    accept_service_purchase = AcceptServicePurchase.Field()
    approve_service_purchase = ApproveServicePurchase.Field()
    deliver_service_purchase = DeliverServicePurchase.Field()
    cancel_service_purchase = CancelServicePurchase.Field()
