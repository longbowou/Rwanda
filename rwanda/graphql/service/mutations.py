import os
import uuid

import graphene
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import ServiceType, AccountType
from rwanda.service.models import ServiceOption, ServiceMedia


class ServiceOptionInput(graphene.InputObjectType):
    label = graphene.String(required=True)
    description = graphene.String()
    delay = graphene.Int(required=True)
    price = graphene.Int(required=True)


class ServiceMediaInput(graphene.InputObjectType):
    file = graphene.String()
    url = graphene.String()


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


class ServiceMutations(graphene.ObjectType):
    create_service = CreateService.Field()
    update_service = UpdateService.Field()
    delete_service = DeleteService.Field()
