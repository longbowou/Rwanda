import graphene

from rwanda.graphql.mutations import DjangoModelMutation, DjangoModelDeleteMutation
from rwanda.graphql.types import ServiceCategoryType


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


class AdminMutations(graphene.ObjectType):
    create_service_category = CreateServiceCategory.Field()
    update_service_category = UpdateServiceCategory.Field()
    delete_service_category = DeleteServiceCategory.Field()
