import graphene
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.administration.utils import param_base_price, param_commission
from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation, AccountDjangoModelDeleteMutation
from rwanda.graphql.purchase.operations import approve_service_purchase, cancel_service_purchase, init_service_purchase
from rwanda.graphql.purchase.subscriptions import ChatSubscription
from rwanda.graphql.types import ServicePurchaseType, DeliverableType, DeliverableFileType, ChatMessageType
from rwanda.purchase.models import ServicePurchase, Deliverable, ChatMessage
from rwanda.user.models import Account


class InitServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ('service', 'service_options')

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        account = Account.objects.select_for_update().get(pk=info.context.user.account.id)

        price = int(param_base_price())
        commission = int(param_commission())

        service = form.instance.service
        delay = service.delay

        for service_option in form.cleaned_data['service_options']:
            price += service_option.price
            delay += service_option.delay

        total_price = price + commission

        if account.balance < total_price:
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

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        instance: Deliverable = form.instance

        if instance.service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if instance.final and instance.published:
            instance.service_purchase.has_final_deliverable = True
            instance.service_purchase.save()

        instance.save()

        return cls(deliverable=instance, errors=[])


class UpdateDeliverable(AccountDjangoModelMutation):
    class Meta:
        model_type = DeliverableType
        for_update = True
        exclude_fields = ("service_purchase",)

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        instance: Deliverable = form.instance

        if instance.service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if instance.final and instance.published:
            if not instance.service_purchase.has_final_deliverable:
                instance.service_purchase.has_final_deliverable = True
                instance.service_purchase.save()
        else:
            has_final_deliverable = Deliverable.objects \
                .filter(version=Deliverable.VERSION_FINAL,
                        service_purchase=instance.service_purchase,
                        published=True) \
                .exclude(id=instance.id) \
                .exists()
            if instance.service_purchase.has_final_deliverable is not has_final_deliverable:
                instance.service_purchase.has_final_deliverable = has_final_deliverable
                instance.service_purchase.save()

        instance.save()

        return cls(deliverable=instance, errors=[])


class DeleteDeliverable(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = DeliverableType

    @classmethod
    @transaction.atomic
    def pre_delete(cls, info, obj):
        obj: Deliverable

        if obj.service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        has_final_deliverable = Deliverable.objects \
            .filter(version=Deliverable.VERSION_FINAL,
                    service_purchase=obj.service_purchase,
                    published=True) \
            .exclude(id=obj.id) \
            .exists()
        if obj.service_purchase.has_final_deliverable is not has_final_deliverable:
            obj.service_purchase.has_final_deliverable = has_final_deliverable
            obj.service_purchase.save()

        obj.delete()

        return cls(errors=[])


class DeleteDeliverableFile(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = DeliverableFileType

    @classmethod
    def pre_delete(cls, info, obj):
        if obj.deliverable.service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class CreateChatMessage(AccountDjangoModelMutation):
    class Meta:
        model_type = ChatMessageType
        only_fields = ('service_purchase', 'content',)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        form.instance.account = info.context.user.account

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        obj: ChatMessage
        ChatSubscription.broadcast(group=ChatSubscription.name.format(obj.service_purchase_id),
                                   payload=obj.id.urn[9:])


class PurchaseMutations(graphene.ObjectType):
    init_service_purchase = InitServicePurchase.Field()
    accept_service_purchase = AcceptServicePurchase.Field()
    approve_service_purchase = ApproveServicePurchase.Field()
    deliver_service_purchase = DeliverServicePurchase.Field()
    cancel_service_purchase = CancelServicePurchase.Field()

    create_deliverable = CreateDeliverable.Field()
    update_deliverable = UpdateDeliverable.Field()
    delete_deliverable = DeleteDeliverable.Field()

    delete_deliverable_file = DeleteDeliverableFile.Field()

    create_chat_message = CreateChatMessage.Field()
