import graphene

from rwanda.graphql.mutations import DjangoModelMutation
from rwanda.graphql.types import ServicePurchaseType


class InitServicePurchase(DjangoModelMutation):
    class Meta:
        model_type = ServicePurchaseType
        only_fields = ("account", 'service', 'service_options')


class PurchaseMutations(graphene.ObjectType):
    init_service_purchase = InitServicePurchase.Field()
