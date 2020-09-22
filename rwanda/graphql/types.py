from datetime import timedelta

import graphene
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.template.defaultfilters import date as date_filter, time as time_filter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from graphene import ObjectType
from graphene_django import DjangoObjectType

from rwanda.account.models import Deposit, Refund
from rwanda.accounting.models import Fund, Operation
from rwanda.administration.models import Parameter
from rwanda.administration.utils import param_base_price
from rwanda.graphql.interfaces import UserInterface
from rwanda.purchase.models import ServicePurchase, ServicePurchaseServiceOption, Chat, Litigation, Deliverable, \
    DeliverableFile
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


class ServiceOptionType(DjangoObjectType):
    price_display = graphene.String(source="price_display", required=True)
    delay_preview_display = graphene.String(source="delay_preview_display", required=True)
    delay_display = graphene.String(source="delay_display", required=True)
    published_display = graphene.String(source="published_display", required=True)

    class Meta:
        model = ServiceOption
        filter_fields = {
            "id": ("exact",),
        }


class ServiceType(DjangoObjectType):
    delay_display = graphene.String(source="delay_display", required=True)
    published_display = graphene.String(source="published_display", required=True)
    options_count = graphene.Int(source="options_count", required=True)
    options_count_display = graphene.String(source="options_count_display", required=True)
    created_at = graphene.String(source="created_at_display", required=True)
    options = graphene.List(ServiceOptionType, required=True)
    base_price = graphene.Int(required=True)

    class Meta:
        model = Service
        filter_fields = {
            "id": ("exact",),
        }

    @staticmethod
    def resolve_options(cls, info):
        cls: Service
        return cls.serviceoption_set.filter(published=True)

    @staticmethod
    def resolve_base_price(cls, info):
        return param_base_price()


class AccountType(DjangoObjectType):
    balance = graphene.String(required=True, source="balance_display")
    services_count = graphene.String(required=True, source="services_count_display")
    purchases_count = graphene.String(required=True, source="purchases_count_display")
    orders_count = graphene.String(required=True, source="orders_count_display")
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


class ServicePurchaseTimeLine(ObjectType):
    happen_at = graphene.String(required=True)
    status = graphene.String(required=True)
    color = graphene.String(required=True)
    description = graphene.String()


class ServicePurchaseType(DjangoObjectType):
    price = graphene.String(source="price_display", required=True)
    delay = graphene.String(source="delay_display", required=True)
    status = graphene.String(source="status_display", required=True)
    deadline_at = graphene.String(source="deadline_at_display")

    number = graphene.String(source="number", required=True)

    initiated = graphene.Boolean(source="initiated", required=True)
    accepted = graphene.Boolean(source="accepted", required=True)
    delivered = graphene.Boolean(source="delivered", required=True)
    approved = graphene.Boolean(source="approved", required=True)
    canceled = graphene.Boolean(source="canceled", required=True)
    in_dispute = graphene.Boolean(source="in_dispute", required=True)
    has_been_accepted = graphene.Boolean(source="has_been_accepted", required=True)

    can_be_accepted = graphene.Boolean(required=True)
    can_be_delivered = graphene.Boolean(required=True)
    can_be_approved = graphene.Boolean(required=True)
    can_be_canceled = graphene.Boolean(required=True)
    can_be_in_dispute = graphene.Boolean(required=True)
    can_add_deliverable = graphene.Boolean(required=True)

    timelines = graphene.List(ServicePurchaseTimeLine, required=True)

    class Meta:
        model = ServicePurchase
        filter_fields = {
            "id": ("exact",),
        }

    def resolve_can_be_accepted(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_accepted and self.is_seller(user.account)

    def resolve_can_be_delivered(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_delivered and self.is_seller(user.account)

    def resolve_can_add_deliverable(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_add_deliverable and self.is_seller(user.account)

    def resolve_can_be_approved(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_approved and self.is_buyer(user.account)

    def resolve_can_be_canceled(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_canceled and self.is_buyer(user.account)

    def resolve_can_be_in_dispute(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_in_dispute and self.is_buyer(user.account)

    def resolve_timelines(self, info):
        self: ServicePurchase

        today = timezone.now()
        yesterday = timezone.now() - timedelta(1)

        d_filter = date_filter
        t_filter = time_filter
        if self.created_at.date() == today.date():
            d_filter = naturalday
            t_filter = naturaltime

        if self.created_at.date() == yesterday.date():
            d_filter = naturalday
            t_filter = time_filter

        happen_at = str(d_filter(self.created_at)) + ' ' + str(t_filter(self.created_at))

        timelines = [ServicePurchaseTimeLine(
            happen_at=happen_at.title(),
            status=_('Initiated'),
            color='dark'
        )]

        last_happen_at = self.created_at

        if self.has_been_canceled and self.has_not_been_accepted:
            happen_at = str(t_filter(self.canceled_at))
            if last_happen_at.date() != self.canceled_at.date():
                happen_at = str(d_filter(self.canceled_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Canceled'),
                color='danger'
            ))

            last_happen_at = self.canceled_at

        if self.has_been_accepted:
            happen_at = str(t_filter(self.accepted_at))
            if last_happen_at.date() != self.accepted_at.date():
                happen_at = str(d_filter(self.created_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Accepted'),
                color='primary',
                description=_('Deadline set to <strong>{}</strong>'.format(
                    date_filter(self.deadline_at))),
            ))

            last_happen_at = self.accepted_at

        for deliverable in self.deliverable_set.filter(published=True) \
                .order_by("created_at") \
                .all():
            happen_at = str(t_filter(deliverable.created_at))
            if last_happen_at.date() != deliverable.created_at.date():
                happen_at = str(d_filter(deliverable.created_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Deliverable Published'),
                color='info',
                description=_('Deliverable <strong>{}</strong> published in version <strong>{}</strong>.'
                              .format(deliverable.title, deliverable.version_display)),
            ))

            last_happen_at = deliverable.created_at

        if self.has_been_canceled and self.has_been_accepted:
            happen_at = str(t_filter(self.canceled_at))
            if last_happen_at.date() != self.canceled_at.date():
                happen_at = str(d_filter(self.canceled_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Canceled'),
                color='danger'
            ))

        if self.has_been_delivered:
            happen_at = str(t_filter(self.delivered_at))
            if last_happen_at.date() != self.delivered_at.date():
                happen_at = str(d_filter(self.delivered_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Delivered'),
                color='warning'
            ))

            last_happen_at = self.delivered_at

        if self.has_been_in_dispute:
            happen_at = str(t_filter(self.in_dispute_at))
            if last_happen_at.date() != self.in_dispute_at.date():
                happen_at = str(d_filter(self.in_dispute_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Canceled'),
                color='info'
            ))

            last_happen_at = self.in_dispute_at

        if self.has_been_canceled and self.has_been_in_dispute:
            happen_at = str(t_filter(self.canceled_at))
            if last_happen_at.date() != self.canceled_at.date():
                happen_at = str(d_filter(self.canceled_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Canceled'),
                color='danger'
            ))

        if self.has_been_approved:
            happen_at = str(t_filter(self.approved_at))
            if last_happen_at.date() != self.approved_at.date():
                happen_at = str(d_filter(self.approved_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLine(
                happen_at=happen_at.title(),
                status=_('Approved'),
                color='success'
            ))

        return timelines


class DeliverableType(DjangoObjectType):
    files_count = graphene.Int(source="files_count", required=True)
    files_count_display = graphene.String(source="files_counts_display", required=True)
    version_display = graphene.String(source="version_display", required=True)

    class Meta:
        model = Deliverable
        filter_fields = {
            "id": ("exact",),
        }


class DeliverableFileType(DjangoObjectType):
    class Meta:
        model = DeliverableFile
        filter_fields = {
            "id": ("exact",),
        }


class DeliverableVersionType(ObjectType):
    label = graphene.String(required=True)
    value = graphene.String(required=True)


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
    deadline_at = graphene.String(required=True)
    total_delay = graphene.String(required=True)
    service = graphene.Field(ServiceType)
    service_options = graphene.List(ServiceOptionType)
