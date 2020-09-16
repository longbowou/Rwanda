import graphene
from graphene import ObjectType
from graphene_django import DjangoObjectType

from rwanda.account.models import Deposit, Refund
from rwanda.accounting.models import Fund, Operation
from rwanda.administration.models import Parameter
from rwanda.graphql.interfaces import UserInterface
from rwanda.purchase.models import ServicePurchase, ServicePurchaseServiceOption, Chat, Litigation
from rwanda.service.models import ServiceCategory, Service, ServiceMedia, ServiceComment, ServiceOption
from rwanda.user.models import Admin, Account


class AuthType(ObjectType):
    token = graphene.String(required=True)
    refresh_token = graphene.String(required=True)
    token_expires_in = graphene.String(required=True)


class ParametersType(ObjectType):
    currency = graphene.String(required=True)
    base_price = graphene.String(required=True)


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
    balance = graphene.String(required=True, source="balance_display")
    services_count = graphene.String(required=True, source="services_count_display")
    purchases_count = graphene.String(required=True, source="purchases_count_display")
    deposits_sum = graphene.String(required=True, source="deposits_sum_display")
    refunds_sum = graphene.String(required=True, source="refunds_sum_display")
    earnings_sum = graphene.String(required=True, source="earnings_sum_display")

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
    price = graphene.String(source="price_display", required=True)
    delay = graphene.String(source="delay_display", required=True)

    class Meta:
        model = ServiceOption
        filter_fields = {
            "id": ("exact",),
        }


class ServicePurchaseType(DjangoObjectType):
    can_be_accepted = graphene.Boolean(required=True)
    can_be_delivered = graphene.Boolean(required=True)
    can_be_approved = graphene.Boolean(required=True)
    can_be_canceled = graphene.Boolean(required=True)
    can_create_litigation = graphene.Boolean(required=True)

    class Meta:
        model = ServicePurchase
        filter_fields = {
            "id": ("exact",),
        }

    def resolve_can_be_accepted(self, info):
        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_accepted and self.is_seller(user.account)

    def resolve_can_be_delivered(self, info):
        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_delivered and self.is_seller(user.account)

    def resolve_can_be_approved(self, info):
        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_approved and self.is_buyer(user.account)

    def resolve_can_be_canceled(self, info):
        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_canceled and self.is_buyer(user.account)


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


class ServiceOrderType(ObjectType):
    total_order_price = graphene.String(required=True)
    total_order_price_ttc = graphene.String(required=True)
    cannot_pay_with_wallet = graphene.Boolean(required=True)
    base_price = graphene.String(required=True)
    commission = graphene.String(required=True)
    commission_tva = graphene.String(required=True)
    total_price = graphene.String(required=True)
    total_price_tva = graphene.String(required=True)
    must_be_delivered_at = graphene.String(required=True)
    total_delay = graphene.String(required=True)
    service = graphene.Field(ServiceType)
    serviceOptions = graphene.List(ServiceOptionType)
