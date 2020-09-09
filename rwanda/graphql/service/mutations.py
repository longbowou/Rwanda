import os
import uuid
from datetime import datetime

import graphene
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from graphene_django.types import ErrorType

from rwanda.graphql.auth_base_mutations.account import AccountDjangoModelMutation, AccountDjangoModelDeleteMutation
from rwanda.graphql.types import ServiceType, ServiceMediaType, AccountType, ServiceCommentType, ServiceOptionType
from rwanda.service.models import ServiceOption, ServiceMedia


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
        exclude_fields = ("activated", "stars")
        extra_input_fields = {
            "service_options": graphene.List(ServiceOptionInput),
            "service_medias": graphene.List(ServiceMediaInput)
        }

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        form.instance.account = info.context.user.account

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        if input.service_options is not None:
            for item in input.service_options:
                ServiceOption(service=obj, **item).save()

        if input.service_medias is not None:
            for item in input.service_medias:
                if item.file is None and item.url is None:
                    continue

                if item.file is not None:
                    f: UploadedFile = info.context.FILES[item.file]
                    if f is not None:
                        file_name = uuid.uuid4().urn[9:] + '.' + f.name.split('.')[1]
                        folder = "service-medias"
                        file_path = os.path.join(settings.BASE_DIR, "media", folder, file_name)

                        with open(file_path, 'wb+') as destination:
                            for chunk in f.chunks():
                                destination.write(chunk)

                        ServiceMedia(service=obj, file=folder + "/" + file_name).save()
                        continue

                if item.url is not None:
                    ServiceMedia(service=obj, url=item.url).save()
                    continue


class UpdateService(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        exclude_fields = ("activated", 'account')

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class DeleteService(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = AccountType

    @classmethod
    def pre_delete(cls, info, obj):
        if obj.account_id != info.context.user.account.id:
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
        only_fields = ("content", "service", "positive")

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.cleaned_data["service"].account_id == info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])

        form.instance.account = info.context.user.account


class UpdateServiceComment(AccountDjangoModelMutation):
    class Meta:
        model_type = ServiceCommentType
        for_update = True
        only_fields = ("content", "positive")

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        if form.instance.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


class DeleteServiceComment(AccountDjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceCommentType

    @classmethod
    def pre_delete(cls, info, obj):
        if obj.account_id != info.context.user.account.id:
            return cls(errors=[ErrorType(field="id", messages=[_("You cannot perform this action.")])])


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

    create_service_media = CreateServiceMedia.Field()
    update_service_media = UpdateServiceMedia.Field()
    delete_service_media = DeleteServiceMedia.Field()

    create_service_comment = CreateServiceComment.Field()
    update_service_comment = UpdateServiceComment.Field()
    delete_service_comment = DeleteServiceComment.Field()
    reply_service_comment = ReplyServiceComment.Field()

    create_service_option = CreateServiceOption.Field()
    update_service_option = UpdateServiceOption.Field()
    delete_service_option = DeleteServiceOption.Field()
