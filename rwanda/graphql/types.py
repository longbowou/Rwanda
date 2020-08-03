from graphene_django import DjangoObjectType

from rwanda.administration.models import Parameters
from rwanda.graphql.interfaces import UserInterface
from rwanda.purchase.models import ServicePurchase, ServicePurchaseServiceOption, Chat, Litigation
from rwanda.service.models import ServiceCategory, Service, ServiceMedia, ServiceComment, ServiceOption
from rwanda.user.models import Admin, Account


class ServiceCategoryType(DjangoObjectType):
    class Meta:
        model = ServiceCategory
        filter_fields = {
            "id": ("exact",),
        }


class ServiceType(DjangoObjectType):
    class Meta:
        model = Service
        filter_fields = {
            "id": ("exact",),
        }


class ParametersType(DjangoObjectType):
    class Meta:
        model = Parameters
        filter_fields = {
            "id": ("exact",),
        }


class AdminType(DjangoObjectType):
    class Meta:
        model = Admin
        interfaces = (UserInterface,)
        filter_fields = {
            "id": ("exact",),
        }


class AccountType(DjangoObjectType):
    class Meta:
        model = Account
        interfaces = (UserInterface,)
        filter_fields = {
            "id": ("exact",),
        }


class ServiceMediaType(DjangoObjectType):
    class Meta:
        model = ServiceMedia
        filter_fields = {
            "id": ("exact",),
        }


class ServiceCommentType(DjangoObjectType):
    class Meta:
        model = ServiceComment
        filter_fields = {
            "id": ("exact",),
        }


class ServiceOptionType(DjangoObjectType):
    class Meta:
        model = ServiceOption
        filter_fields = {
            "id": ("exact",),
        }


class ServicePurchaseType(DjangoObjectType):
    class Meta:
        model = ServicePurchase
        filter_fields = {
            "id": ("exact",),
        }


class ServicePurchaseServiceOptionType(DjangoObjectType):
    class Meta:
        model = ServicePurchaseServiceOption
        filter_fields = {
            "id": ("exact",),
        }


class ChatType(DjangoObjectType):
    class Meta:
        model = Chat
        filter_fields = {
            "id": ("exact",),
        }


class LitigationType(DjangoObjectType):
    class Meta:
        model = Litigation
        filter_fields = {
            "id": ("exact",),
        }
