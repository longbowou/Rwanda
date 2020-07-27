from graphene_django import DjangoObjectType

from rwanda.core.models import ServiceCategory


class ServiceCategoryType(DjangoObjectType):
    class Meta:
        model = ServiceCategory
        filter_fields = {
            "id": ("exact",),
        }
