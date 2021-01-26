import graphene
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.account.tasks import on_service_purchase_initiated_task, on_service_purchase_approved_task, \
    on_service_purchase_delivered_task, on_service_purchase_accepted_or_refused_task, \
    on_service_purchase_update_request_delivered_task, \
    on_service_purchase_update_request_accepted_or_refused_task, \
    on_service_purchase_update_request_initiated_task, on_service_purchase_canceled_task
from rwanda.administration.utils import param_base_price, param_commission
from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation, AccountDjangoModelDeleteMutation
from rwanda.graphql.decorators import account_required
from rwanda.graphql.purchase.operations import approve_service_purchase, cancel_service_purchase, init_service_purchase
from rwanda.graphql.purchase.subscriptions import ChatMessageSubscription, ServicePurchaseSubscription
from rwanda.graphql.types import ServicePurchaseType, DeliverableType, DeliverableFileType, ChatMessageType, \
    ServicePurchaseUpdateRequestType
from rwanda.purchase.models import ServicePurchase, Deliverable, ChatMessage, ChatMessageMarked, \
    ServicePurchaseUpdateRequest
from rwanda.user.models import Account


class InitiateServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ('service', 'service_options')

    @classmethod
    @transaction.atomic
    def pre_save(cls, info, old_obj, form, input):
        account = Account.objects.select_for_update().get(pk=info.context.user.account.id)

        base_price = param_base_price()

        service_purchase: ServicePurchase = form.instance
        service = service_purchase.service
        delay = service.delay

        price = base_price
        for service_option in form.cleaned_data['service_options']:
            price += service_option.price
            delay += service_option.delay

        total_price = price
        commission = price * param_commission()

        if account.balance < total_price:
            return cls(
                errors=[ErrorType(field="service", messages=[_("Insufficient amount to purchase service.")])])

        service_purchase.account = account
        service_purchase.base_price = base_price
        service_purchase.price = price
        service_purchase.delay = delay
        service_purchase.commission = commission

        init_service_purchase(service_purchase)

        form.save()
        form.instance.refresh_from_db()

        on_service_purchase_initiated_task.delay(str(form.instance.id))

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

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        ServicePurchaseSubscription.broadcast(group=ServicePurchaseSubscription.name.format(str(obj.id)))

        on_service_purchase_accepted_or_refused_task.delay(str(obj.id))


class RefuseServicePurchase(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        for_update = True
        only_fields = ("refused_reason",)
        custom_input_fields = {"refused_reason": graphene.String(required=True)}

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service_purchase: ServicePurchase = form.instance

        if service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        if service_purchase.cannot_be_refused:
            return cls(
                errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])],
                servicePurchase=service_purchase)

        service_purchase.set_as_refused()

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        ServicePurchaseSubscription.broadcast(group=ServicePurchaseSubscription.name.format(str(obj.id)))

        on_service_purchase_accepted_or_refused_task.delay(str(obj.id))


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

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        ServicePurchaseSubscription.broadcast(group=ServicePurchaseSubscription.name.format(str(obj.id)))

        on_service_purchase_delivered_task.delay(str(obj.id))


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
        service_purchase.save()
        service_purchase.refresh_from_db()

        ServicePurchaseSubscription.broadcast(group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_service_purchase_approved_task.delay(str(service_purchase.id))

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

        ServicePurchaseSubscription.broadcast(group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_service_purchase_canceled_task.delay(str(service_purchase.id))

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
        ChatMessageSubscription.broadcast(group=ChatMessageSubscription.name.format(obj.service_purchase_id),
                                          payload=str(obj.id))


class MarkUnmarkChatMessage(graphene.Mutation):
    class Arguments:
        chat_message = graphene.UUID(required=True)

    marked = graphene.Boolean(required=True)

    @account_required
    def mutate(self, info, chat_message):
        account = info.context.user.account

        chat_message_marked = ChatMessageMarked.objects. \
            filter(chat_message=chat_message, account=account) \
            .first()

        if chat_message_marked is not None:
            chat_message_marked.delete()
            return MarkUnmarkChatMessage(marked=False)

        ChatMessageMarked(chat_message_id=chat_message, account=account).save()

        return MarkUnmarkChatMessage(marked=True)


class InitiateServicePurchaseUpdateRequest(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseUpdateRequestType
        only_fields = ('title', 'content', 'service_purchase')

    @classmethod
    @transaction.atomic()
    def pre_save(cls, info, old_obj, form, input):
        update_request: ServicePurchaseUpdateRequest = form.instance
        service_purchase: ServicePurchase = form.cleaned_data['service_purchase']

        if service_purchase.cannot_ask_for_update or service_purchase.is_not_buyer(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        service_purchase.set_as_update_initiated()
        service_purchase.save()

        update_request.save()

        ServicePurchaseSubscription.broadcast(
            group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_service_purchase_update_request_initiated_task.delay(str(update_request.id))

        return cls(servicePurchaseUpdateRequest=update_request, errors=[])


class AcceptServicePurchaseUpdateRequest(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseUpdateRequestType
        only_fields = ("",)
        for_update = True

    @classmethod
    @transaction.atomic()
    def pre_save(cls, info, old_obj, form, input):
        update_request: ServicePurchaseUpdateRequest = form.instance
        service_purchase: ServicePurchase = update_request.service_purchase

        if update_request.cannot_be_accepted or service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        service_purchase.set_as_update_accepted()
        service_purchase.save()

        update_request.set_as_accepted()
        update_request.deadline_at = service_purchase.deadline_at
        update_request.save()

        ServicePurchaseSubscription.broadcast(
            group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_service_purchase_update_request_accepted_or_refused_task.delay(str(update_request.id))

        return cls(servicePurchaseUpdateRequest=update_request, errors=[])


class RefuseServicePurchaseUpdateRequest(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseUpdateRequestType
        only_fields = ("reason",)
        custom_input_fields = {'reason': graphene.String(required=True)}
        for_update = True

    @classmethod
    @transaction.atomic()
    def pre_save(cls, info, old_obj, form, input):
        update_request: ServicePurchaseUpdateRequest = form.instance
        service_purchase: ServicePurchase = update_request.service_purchase

        if update_request.cannot_be_refused or service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        service_purchase.set_as_update_refused()
        service_purchase.save()

        update_request.set_as_refused()
        update_request.save()

        ServicePurchaseSubscription.broadcast(
            group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_service_purchase_update_request_accepted_or_refused_task.delay(str(update_request.id))

        return cls(servicePurchaseUpdateRequest=update_request, errors=[])


class DeliverServicePurchaseUpdateRequest(AccountDjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseUpdateRequestType
        only_fields = ("",)
        for_update = True

    @classmethod
    @transaction.atomic()
    def pre_save(cls, info, old_obj, form, input):
        update_request: ServicePurchaseUpdateRequest = form.instance
        service_purchase: ServicePurchase = update_request.service_purchase

        if update_request.cannot_be_delivered or service_purchase.is_not_seller(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        service_purchase.set_as_update_delivered()
        service_purchase.save()

        update_request.set_as_delivered()
        update_request.save()

        ServicePurchaseSubscription.broadcast(
            group=ServicePurchaseSubscription.name.format(str(service_purchase.id)))

        on_service_purchase_update_request_delivered_task.delay(str(update_request.id))

        return cls(servicePurchaseUpdateRequest=update_request, errors=[])


class PurchaseMutations(graphene.ObjectType):
    initiate_service_purchase = InitiateServicePurchase.Field()
    accept_service_purchase = AcceptServicePurchase.Field()
    refuse_service_purchase = RefuseServicePurchase.Field()
    approve_service_purchase = ApproveServicePurchase.Field()
    deliver_service_purchase = DeliverServicePurchase.Field()
    cancel_service_purchase = CancelServicePurchase.Field()

    create_deliverable = CreateDeliverable.Field()
    update_deliverable = UpdateDeliverable.Field()
    delete_deliverable = DeleteDeliverable.Field()

    delete_deliverable_file = DeleteDeliverableFile.Field()

    create_chat_message = CreateChatMessage.Field()
    mark_unmark_chat_message = MarkUnmarkChatMessage.Field()

    initiate_service_purchase_update_request = InitiateServicePurchaseUpdateRequest.Field()
    accept_service_purchase_update_request = AcceptServicePurchaseUpdateRequest.Field()
    refuse_service_purchase_update_request = RefuseServicePurchaseUpdateRequest.Field()
    deliver_service_purchase_update_request = DeliverServicePurchaseUpdateRequest.Field()
