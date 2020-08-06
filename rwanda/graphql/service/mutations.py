import graphene

from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import ServiceType
from rwanda.service.models import ServiceOption


class ServiceOptionInput(graphene.InputObjectType):
    label = graphene.String(required=True)
    description = graphene.String()
    delay = graphene.Int(required=True)
    price = graphene.Int(required=True)


class CreateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        exclude_fields = ("activated", "stars")
        extra_input_fields = {"service_options": graphene.List(ServiceOptionInput)}

    @classmethod
    def post_mutate(cls, old_obj, form, obj, input):
        if input.service_options is not None:
            for item in input.service_options:
                ServiceOption(service=obj, **item).save()


class UpdateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        for_update = True
        exclude_fields = ("activated", 'account')


class DeleteService(DjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceType


class ServiceMutations(graphene.ObjectType):
    create_service = CreateService.Field()
    update_service = UpdateService.Field()
    delete_service = DeleteService.Field()
