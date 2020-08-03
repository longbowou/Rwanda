import graphene

from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import ServiceType, AccountType


class CreateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        exclude_fields = ("activated",)


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
