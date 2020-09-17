import graphene

from rwanda.graphql.types import ServicePurchaseType, LitigationType
from rwanda.purchase.models import ServicePurchase, Litigation


class PurchaseQueries(graphene.ObjectType):
    litigation = graphene.Field(LitigationType, required=True, id=graphene.UUID(required=True))
    service_purchase = graphene.Field(ServicePurchaseType, required=True, id=graphene.UUID(required=True))

    def resolve_litigation(self, info, id):
        return Litigation.objects.get(pk=id)

    def resolve_service_purchase(self, info, id):
        return ServicePurchase.objects.get(pk=id)
