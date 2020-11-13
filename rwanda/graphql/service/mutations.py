from datetime import datetime

import graphene
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation, AccountDjangoModelDeleteMutation
from rwanda.graphql.types import ServiceType, ServiceMediaType, ServiceCommentType, ServiceOptionType
from rwanda.service.models import ServiceMedia, ServiceComment, Service


# INPUTS
class ServiceOptionInput(graphene.InputObjectType):
    label = graphene.String(required=True)
    description = graphene.String()
    delay = graphene.Int(required=True)
    price = graphene.Int(required=True)


class ServiceMediaInput(graphene.InputObjectType):
    file = graphene.String()
    url = graphene.String()


# SERVICE MUTATIONS
class CreateService(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceType
        exclude_fields = ("activated", "stars", "account")

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        service: Service = form.instance
        service.account = info.context.user.account

        if input.file != None:
            service.file = input.file

        service.save()

        service.refresh_from_db()

        return cls(service=service, errors=[])


class UpdateService(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        exclude_fields = ("activated", 'account')

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.is_not_owner(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class DeleteService(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceType

    @classmethod
    def pre_delete(cls, info, obj):
        if obj.is_not_owner(info.context.user.account):
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


# SERVICE MEDIA MUTATIONS
class CreateServiceMedia(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceMediaType

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.cleaned_data["service"].account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        if input.is_main is not None and obj.is_main:
            ServiceMedia.objects.exclude(pk=input.id).update(is_main=False)


class UpdateServiceMedia(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceMediaType
        for_update = True
        exclude_fields = ('service',)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.service.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        if input.is_main is not None and obj.is_main:
            ServiceMedia.objects.exclude(pk=input.id).update(is_main=False)


class DeleteServiceMedia(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceMediaType

    @classmethod
    def pre_delete(cls, info, obj):
        if obj.service.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


# SERVICE OPTIONS MUTATION
class CreateServiceOption(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceOptionType

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.cleaned_data["service"].account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class UpdateServiceOption(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceOptionType
        for_update = True
        exclude_fields = ('service',)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.service.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class DeleteServiceOption(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceOptionType

    @classmethod
    def pre_delete(cls, info, obj):
        if obj.service.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


# SERVICE COMMENT MUTATIONS
class CreateServiceComment(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceCommentType
        only_fields = ("content", "type", "service_purchase")
        custom_input_fields = {
            "service_purchase": graphene.UUID(required=True),
            "type": graphene.String(required=True)
        }

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        comment: ServiceComment = form.instance
        comment.account = info.context.user.account


class ReplyServiceComment(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceCommentType
        for_update = True
        only_fields = ("reply_content",)

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.service.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        form.instance.reply_at = datetime.today()


class ServiceMutations(graphene.ObjectType):
    create_service = CreateService.Field()
    update_service = UpdateService.Field()
    delete_service = DeleteService.Field()

    create_service_comment = CreateServiceComment.Field()

    create_service_option = CreateServiceOption.Field()
    update_service_option = UpdateServiceOption.Field()
    delete_service_option = DeleteServiceOption.Field()
