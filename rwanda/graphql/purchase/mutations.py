import graphene
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.administration.models import Parameter
from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation, AccountDjangoModelDeleteMutation
from rwanda.graphql.purchase.operations import approve_service_purchase, cancel_service_purchase, init_service_purchase
from rwanda.graphql.types import ServicePurchaseType, DeliverableType
from rwanda.purchase.models import ServicePurchase
from rwanda.user.models import Account


class InitServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ('service', 'service_options')

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        account = Account.objects.select_for_update().get(pk=info.context.user.account.id)

        price = int(Parameter.objects.get(label=Parameter.BASE_PRICE).value)
        commission = int(Parameter.objects.get(label=Parameter.COMMISSION).value)

        service = form.instance.service
        delay = service.delay

        for service_option in form.cleaned_data['service_options']:
            price += service_option.price
            delay += service_option.delay

        if account.balance < price:
            return cls(
                errors=[ErrorType(field="service", messages=[_("Insufficient amount to purchase service.")])])

        form.instance.account = account
        form.instance.price = price
        form.instance.delay = delay
        form.instance.commission = commission

        init_service_purchase(form.instance)

        form.save()
        form.instance.refresh_from_db()

        return cls(servicePurchase=form.instance, errors=[])


class AcceptServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_accepted:
            return cls(
                errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])],
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

        if service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_delivered:
            return cls(
                errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])],
                servicePurchase=service_purchase)

        service_purchase.set_as_delivered()


class ApproveServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.is_not_buyer(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_approved:
            return cls(
                errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])],
                servicePurchase=service_purchase)

        approve_service_purchase(service_purchase)

        service_purchase.set_as_approved()
        form.save()
        service_purchase.refresh_from_db()

        return cls(servicePurchase=service_purchase, errors=[])


class CancelServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("",)
        for_update = True

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.is_not_buyer(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_canceled:
            return cls(
                errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])],
                servicePurchase=service_purchase)

        cancel_service_purchase(service_purchase)

        service_purchase.set_as_canceled()
        form.save()
        service_purchase.refresh_from_db()

        return cls(servicePurchase=service_purchase, errors=[])


class CreateDeliverable(AccountDjangoModelMutation):
    class Meta:
        model_type = DeliverableType
        exclude_fields = ("published",)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class UpdateDeliverable(AccountDjangoModelMutation):
    class Meta:
        model_type = DeliverableType
        for_update = True
        exclude_fields = ("service_purchase",)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class DeleteDeliverable(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = DeliverableType

    @classmethod
    def pre_delete(cls, info, obj):
        if obj.service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class PurchaseMutations(graphene.ObjectType):
    init_service_purchase = InitServicePurchase.Field()
    accept_service_purchase = AcceptServicePurchase.Field()
    approve_service_purchase = ApproveServicePurchase.Field()
    deliver_service_purchase = DeliverServicePurchase.Field()
    cancel_service_purchase = CancelServicePurchase.Field()

    create_deliverable = CreateDeliverable.Field()
    update_deliverable = UpdateDeliverable.Field()
    delete_deliverable = DeleteDeliverable.Field()
