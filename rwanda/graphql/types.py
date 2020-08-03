from graphene_django import DjangoObjectType

from rwanda.core.models import ServiceCategory, Service, Parameters, Admin, Account, ServiceMedia, Comment, \
    ServiceOption, SellerPurchase, SellerPurchaseServiceOption, Chat, Litigation
from rwanda.graphql.interfaces import UserInterface


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


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = {
            "id": ("exact",),
        }


class ServiceOptionType(DjangoObjectType):
    class Meta:
        model = ServiceOption
        filter_fields = {
            "id": ("exact",),
        }


class SellerPurchaseType(DjangoObjectType):
    class Meta:
        model = SellerPurchase
        filter_fields = {
            "id": ("exact",),
        }


class SellerPurchaseServiceOptionType(DjangoObjectType):
    class Meta:
        model = SellerPurchaseServiceOption
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
