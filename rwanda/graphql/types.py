import graphene
from graphene_django import DjangoObjectType

from rwanda.account.models import Deposit, Refund
from rwanda.accounting.models import Fund, Operation
from rwanda.administration.models import Parameter
from rwanda.graphql.interfaces import UserInterface
from rwanda.purchase.models import ServicePurchase, ServicePurchaseServiceOption, Chat, Litigation
from rwanda.service.models import ServiceCategory, Service, ServiceMedia, ServiceComment, ServiceOption
from rwanda.user.models import Admin, Account


class DepositType(DjangoObjectType):
    class Meta:
        model = Deposit
        filter_fields = {
            "id": ("exact",),
        }


class RefundType(DjangoObjectType):
    class Meta:
        model = Refund
        filter_fields = {
            "id": ("exact",),
        }


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


class AccountType(DjangoObjectType):
    class Meta:
        model = Account
        interfaces = (UserInterface,)
        filter_fields = {
            "id": ("exact",),
        }


class ServiceMediaType(DjangoObjectType):
    file_url = graphene.String()

    class Meta:
        model = ServiceMedia
        exclude = ('file',)
        filter_fields = {
            "id": ("exact",),
        }

    @staticmethod
    def resolve_file_url(cls, info):
        return info.context.scheme + "://" + info.context.META['HTTP_HOST'] + cls.file_url if cls.file_url else None


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
    can_be_accepted = graphene.Boolean(required=True, source='can_be_accepted')
    can_be_delivered = graphene.Boolean(required=True, source='can_be_delivered')
    can_be_approved = graphene.Boolean(required=True, source='can_be_approved')
    can_be_canceled = graphene.Boolean(required=True, source='can_be_canceled')
    can_create_litigation = graphene.Boolean(required=True, source='can_create_litigation')

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


class ParameterType(DjangoObjectType):
    class Meta:
        model = Parameter
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


class FundType(DjangoObjectType):
    class Meta:
        model = Fund
        filter_fields = {
            "id": ("exact",),
        }


class OperationType(DjangoObjectType):
    class Meta:
        model = Operation
        filter_fields = {
            "id": ("exact",),
        }
