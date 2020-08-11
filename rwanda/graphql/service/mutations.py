import os
import uuid
from datetime import datetime

import graphene
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
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
class CreateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        exclude_fields = ("activated", "stars")
        extra_input_fields = {
            "service_options": graphene.List(ServiceOptionInput),
            "service_medias": graphene.List(ServiceMediaInput)
        }

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
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


class UpdateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        exclude_fields = ("activated", 'account')


class DeleteService(DjangoModelDeleteMutation):
    class Meta:
        model_type = AccountType


# SERVICE MEDIA MUTATIONS
class CreateServiceMedia(DjangoModelMutation):
    class Meta:
        model_type = ServiceMediaType

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        if input.is_main is not None and obj.is_main:
            ServiceMedia.objects.exclude(pk=input.id).update(is_main=False)


class UpdateServiceMedia(DjangoModelMutation):
    class Meta:
        model_type = ServiceMediaType
        for_update = True
        exclude_fields = ('service',)

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        if input.is_main is not None and obj.is_main:
            ServiceMedia.objects.exclude(pk=input.id).update(is_main=False)


class DeleteServiceMedia(DjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceMediaType


# SERVICE COMMENT MUTATIONS
class CreateServiceComment(DjangoModelMutation):
    class Meta:
        model_type = ServiceCommentType
        only_fields = ("content", "account", "service", "positive")


class UpdateServiceComment(DjangoModelMutation):
    class Meta:
        model_type = ServiceCommentType
        for_update = True
        only_fields = ("content", "positive")


class DeleteServiceComment(DjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceCommentType


class ReplyServiceComment(DjangoModelMutation):
    class Meta:
        model_type = ServiceCommentType
        for_update = True
        only_fields = ("reply_content",)

    @classmethod
    def pre_mutate(cls, info, old_obj, form, input):
        form.instance.reply_at = datetime.today()


# SERVICE OPTIONS MUTATION
class CreateServiceOption(DjangoModelMutation):
    class Meta:
        model_type = ServiceOptionType

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        pass


class UpdateServiceOption(DjangoModelMutation):
    class Meta:
        model_type = ServiceOptionType
        for_update = True
        exclude_fields = ('service',)

    @classmethod
    def post_mutate(cls, info, old_obj, form, obj, input):
        pass


class DeleteServiceOption(DjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceOptionType


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
