import graphene
from django.utils.translation import gettext_lazy as _

from rwanda.graphql.types import ServicePurchaseType, LitigationType, DeliverableType, DeliverableVersionType, \
    ServiceCommentTypeType
from rwanda.purchase.models import ServicePurchase, Litigation, Deliverable
from rwanda.service.models import ServiceComment


class PurchaseQueries(graphene.ObjectType):
    litigation = graphene.Field(LitigationType, required=True, id=graphene.UUID(required=True))
    service_purchase = graphene.Field(ServicePurchaseType, required=True, id=graphene.UUID(required=True))
    deliverable = graphene.Field(DeliverableType, required=True, id=graphene.UUID(required=True))
    deliverable_versions = graphene.List(graphene.NonNull(DeliverableVersionType), required=True)
    service_comment_types = graphene.List(ServiceCommentTypeType)

    def resolve_litigation(self, info, id):
        return Litigation.objects.get(pk=id)

    def resolve_service_comment_types(self, info):
        return [
            ServiceCommentTypeType(name=_("Positive"), value=ServiceComment.TYPE_POSITIVE),
            ServiceCommentTypeType(name=_("Negative"), value=ServiceComment.TYPE_NEGATIVE),
        ]

    def resolve_service_purchase(self, info, id):
        return ServicePurchase.objects.get(pk=id)

    def resolve_deliverable(self, info, id):
        return Deliverable.objects.get(pk=id)

    def resolve_deliverable_versions(self, info):
        versions = [
            DeliverableVersionType(label=_('Alpha'), value=Deliverable.VERSION_ALPHA),
            DeliverableVersionType(label=_('Beta'), value=Deliverable.VERSION_BETA),
            DeliverableVersionType(label=_('Final'), value=Deliverable.VERSION_FINAL)
        ]
        return versions
