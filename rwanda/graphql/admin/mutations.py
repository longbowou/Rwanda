import graphene

from rwanda.graphql.account.mutations import CreateService, DeleteService
from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import ServiceCategoryType, ServiceType


class CreateServiceCategory(DjangoModelMutation):
    class Meta:
        model_type = ServiceCategoryType


class UpdateServiceCategory(DjangoModelMutation):
    class Meta:
        model_type = ServiceCategoryType
        for_update = True


class DeleteServiceCategory(DjangoModelDeleteMutation):
    class Meta:
        model_type = ServiceCategoryType


class UpdateService(DjangoModelMutation):
    class Meta:
        model_type = ServiceType
        only_fields = ('activated',)
        for_update = True


class AdminMutations(graphene.ObjectType):
    create_service_category = CreateServiceCategory.Field()
    update_service_category = UpdateServiceCategory.Field()
    delete_service_category = DeleteServiceCategory.Field()
    create_service = CreateService.Field()
    update_service = UpdateService.Field()
    delete_service = DeleteService.Field()

    update_service = UpdateService.Field()
