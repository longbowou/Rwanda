from datetime import timedelta

import graphene
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime, intcomma
from django.db.models import Case, When, BooleanField, Q
from django.template.defaultfilters import date as date_filter, time as time_filter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from graphene import ObjectType
from graphene_django import DjangoObjectType

from rwanda.account.models import Deposit, Refund, RefundWay
from rwanda.accounting.models import Fund, Operation
from rwanda.administration.models import Parameter
from rwanda.administration.utils import param_base_price
from rwanda.graphql.decorators import account_required, admin_required
from rwanda.graphql.interfaces import UserInterface
from rwanda.payments.models import Payment
from rwanda.purchase.models import ServicePurchase, ServicePurchaseServiceOption, ChatMessage, Litigation, Deliverable, \
    DeliverableFile, ServicePurchaseUpdateRequest
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


class PaymentType(DjangoObjectType):
    confirmed = graphene.Boolean(source="confirmed", required=True)
    canceled = graphene.Boolean(source="canceled", required=True)

    class Meta:
        model = Payment
        filter_fields = {
            "id": ("exact",),
        }


class RefundType(DjangoObjectType):
    class Meta:
        model = Refund
        filter_fields = {
            "id": ("exact",),
        }


class RefundWayType(DjangoObjectType):
    class Meta:
        model = RefundWay
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


class ServiceCommentType(DjangoObjectType):
    created_at = graphene.String(source="created_at_display", required=True)
    positive = graphene.Boolean(source="positive", required=True)
    negative = graphene.Boolean(source="negative", required=True)

    class Meta:
        model = ServiceComment
        filter_fields = {
            "id": ("exact",),
        }


class ServiceType(DjangoObjectType):
    delay_display = graphene.String(source="delay_display", required=True)
    status = graphene.String(source="status_display", required=True)
    options_count = graphene.Int(source="options_count", required=True)
    options_count_display = graphene.String(source="options_count_display", required=True)
    created_at = graphene.String(source="created_at_display", required=True)
    base_price = graphene.Int(required=True)
    file_url = graphene.String(source="file_url")

    accepted = graphene.Boolean(source="accepted", required=True)
    rejected = graphene.Boolean(source="rejected", required=True)
    submitted_for_approval = graphene.Boolean(source="submitted_for_approval", required=True)
    can_be_accepted = graphene.Boolean(source="can_be_accepted", required=True)
    can_be_rejected = graphene.Boolean(source="can_be_rejected", required=True)
    can_be_submitted_for_approval = graphene.Boolean(source="can_be_submitted_for_approval", required=True)

    options = graphene.List(ServiceOptionType, required=True)
    comments = graphene.List(ServiceCommentType)
    positive_comments_count = graphene.String(required=True)
    negative_comments_count = graphene.String(required=True)

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
    def resolve_comments(cls, info):
        cls: Service
        return ServiceComment.objects.order_by("-created_at").filter(service_purchase__service=cls).all()

    @staticmethod
    def resolve_positive_comments_count(cls, info):
        cls: Service
        return intcomma(ServiceComment.objects
                        .filter(service_purchase__service=cls, type=ServiceComment.TYPE_POSITIVE)
                        .count())

    @staticmethod
    def resolve_negative_comments_count(cls, info):
        cls: Service
        return intcomma(ServiceComment.objects
                        .filter(service_purchase__service=cls, type=ServiceComment.TYPE_NEGATIVE)
                        .count())

    @staticmethod
    def resolve_base_price(cls, info):
        return param_base_price()


class ServiceCategoryType(DjangoObjectType):
    services = graphene.List(ServiceType, required=True)

    class Meta:
        model = ServiceCategory
        filter_fields = {
            "id": ("exact",),
        }

    def resolve_services(self, info):
        self: ServiceCategory

        return self.service_set.filter(published=True, status=Service.STATUS_ACCEPTED).all()


class AccountType(DjangoObjectType):
    balance = graphene.String(required=True, source="balance_display")
    created_at = graphene.String(required=True, source="created_at_display")
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
    file_url = graphene.String(source="file_url")

    class Meta:
        model = ServiceMedia
        exclude = ('file',)
        filter_fields = {
            "id": ("exact",),
        }


class ServiceCommentTypeType(graphene.ObjectType):
    name = graphene.String(required=True)
    value = graphene.String(required=True)


class ServicePurchaseTimeLineType(ObjectType):
    happen_at = graphene.String(required=True)
    status = graphene.String(required=True)
    color = graphene.String(required=True)
    description = graphene.String()


class ServicePurchaseChatMessageType(ObjectType):
    id = graphene.UUID(required=True)
    is_file = graphene.Boolean(required=True)
    from_current_account = graphene.Boolean(required=True)
    from_buyer = graphene.Boolean(required=True)
    marked = graphene.Boolean(required=True)
    show_date = graphene.Boolean(required=True)
    time = graphene.String(required=True)
    date = graphene.Int(required=True)
    date_display = graphene.String(required=True)
    created_at = graphene.Float(required=True)
    content = graphene.String()
    file_name = graphene.String()
    file_url = graphene.String()
    file_size = graphene.String()


class ServicePurchaseUpdateRequestType(DjangoObjectType):
    status = graphene.String(source="status_display", required=True)
    initiated = graphene.Boolean(source="initiated", required=True)
    accepted = graphene.Boolean(source="accepted", required=True)
    refused = graphene.Boolean(source="refused", required=True)
    delivered = graphene.Boolean(source="delivered", required=True)
    deadline_at = graphene.String(source="deadline_at_display")

    can_be_accepted = graphene.Boolean(required=True)
    can_be_refused = graphene.Boolean(required=True)
    can_be_delivered = graphene.Boolean(required=True)

    class Meta:
        model = ServicePurchaseUpdateRequest
        filter_fields = {
            "id": ("exact",),
        }

    def resolve_can_be_accepted(self, info):
        self: ServicePurchaseUpdateRequest

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_accepted and self.service_purchase.is_seller(user.account)

    def resolve_can_be_refused(self, info):
        self: ServicePurchaseUpdateRequest

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_refused and self.service_purchase.is_seller(user.account)

    def resolve_can_be_delivered(self, info):
        self: ServicePurchaseUpdateRequest

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_delivered and self.service_purchase.is_seller(user.account)


class ServicePurchaseType(DjangoObjectType):
    price = graphene.String(source="price_display", required=True)
    base_price = graphene.String(source="base_price_display", required=True)
    delay = graphene.String(source="delay_display", required=True)
    status = graphene.String(source="status_display", required=True)
    deadline_at = graphene.String(source="deadline_at_display")

    number = graphene.String(source="number", required=True)

    initiated = graphene.Boolean(source="initiated", required=True)
    accepted = graphene.Boolean(source="accepted", required=True)
    refused = graphene.Boolean(source="refused", required=True)
    delivered = graphene.Boolean(source="delivered", required=True)
    approved = graphene.Boolean(source="approved", required=True)
    update_initiated = graphene.Boolean(source="update_initiated", required=True)
    update_accepted = graphene.Boolean(source="update_accepted", required=True)
    update_refused = graphene.Boolean(source="update_refused", required=True)
    update_delivered = graphene.Boolean(source="update_delivered", required=True)
    canceled = graphene.Boolean(source="canceled", required=True)
    in_dispute = graphene.Boolean(source="in_dispute", required=True)
    has_been_accepted = graphene.Boolean(source="has_been_accepted", required=True)
    can_chat = graphene.Boolean(source="can_chat", required=True)

    can_be_accepted = graphene.Boolean(required=True)
    can_be_refused = graphene.Boolean(required=True)
    can_be_delivered = graphene.Boolean(required=True)
    can_be_approved = graphene.Boolean(required=True)
    can_be_canceled = graphene.Boolean(required=True)
    can_be_in_dispute = graphene.Boolean(required=True)
    can_add_deliverable = graphene.Boolean(required=True)
    can_ask_for_update = graphene.Boolean(required=True)
    can_be_commented = graphene.Boolean(required=True)

    timelines = graphene.List(ServicePurchaseTimeLineType, required=True)
    chat = graphene.List(ServicePurchaseChatMessageType, required=True)
    chat_files = graphene.List(ServicePurchaseChatMessageType, required=True)
    chat_marked = graphene.List(ServicePurchaseChatMessageType, required=True)

    chat_history = graphene.List(ServicePurchaseChatMessageType, required=True)
    chat_files_history = graphene.List(ServicePurchaseChatMessageType, required=True)

    update_request = graphene.Field(ServicePurchaseUpdateRequestType)

    last_update_request = graphene.Field(ServicePurchaseUpdateRequestType)

    class Meta:
        model = ServicePurchase
        filter_fields = {
            "id": ("exact",),
        }

    def resolve_update_request(self, info):
        self: ServicePurchase

        return ServicePurchaseUpdateRequest.objects \
            .filter(service_purchase=self) \
            .exclude(Q(status=ServicePurchaseUpdateRequest.STATUS_DELIVERED) |
                     Q(status=ServicePurchaseUpdateRequest.STATUS_REFUSED)) \
            .first()

    def resolve_last_update_request(self, info):
        self: ServicePurchase

        if self.update_refused or self.update_delivered:
            return ServicePurchaseUpdateRequest.objects \
                .filter(service_purchase=self) \
                .order_by("-created_at") \
                .first()

    def resolve_can_be_accepted(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_accepted and self.is_seller(user.account)

    def resolve_can_be_refused(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_refused and self.is_seller(user.account)

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

    def resolve_can_ask_for_update(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_ask_for_update and self.is_buyer(user.account)

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

    def resolve_can_be_commented(self, info):
        self: ServicePurchase

        user = info.context.user
        if user.is_anonymous or user.is_authenticated and user.is_not_account:
            return False

        return self.can_be_commented and self.is_buyer(user.account)

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

        timelines = [ServicePurchaseTimeLineType(
            happen_at=happen_at.title(),
            status=_('Initiated'),
            color='dark'
        )]

        last_happen_at = self.created_at

        if self.has_been_canceled and self.has_not_been_accepted:
            happen_at = str(t_filter(self.canceled_at))
            if last_happen_at.date() != self.canceled_at.date():
                happen_at = str(d_filter(self.canceled_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLineType(
                happen_at=happen_at.title(),
                status=_('Canceled'),
                color='danger'
            ))

            last_happen_at = self.canceled_at

        if self.has_been_accepted:
            happen_at = str(t_filter(self.accepted_at))
            if last_happen_at.date() != self.accepted_at.date():
                happen_at = str(d_filter(self.created_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLineType(
                happen_at=happen_at.title(),
                status=_('Accepted'),
                color='primary',
                description=_('Deadline set to <strong>{}</strong>')
                    .format(date_filter(self.deadline_at)),
            ))

            last_happen_at = self.accepted_at

        if self.has_been_refused:
            happen_at = str(t_filter(self.refused_at))
            if last_happen_at.date() != self.refused_at.date():
                happen_at = str(d_filter(self.refused_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLineType(
                happen_at=happen_at.title(),
                status=_('Refused'),
                color='danger'
            ))

            last_happen_at = self.accepted_at

        for deliverable in self.deliverable_set.filter(published=True) \
                .order_by("created_at") \
                .all():
            happen_at = str(t_filter(deliverable.created_at))
            if last_happen_at.date() != deliverable.created_at.date():
                happen_at = str(d_filter(deliverable.created_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLineType(
                happen_at=happen_at.title(),
                status=_('Deliverable Published'),
                color='info',
                description=_('Deliverable <strong>{}</strong> published in version <strong>{}</strong>.')
                    .format(deliverable.title, deliverable.version_display),
            ))

            last_happen_at = deliverable.created_at

        if self.has_been_delivered:
            happen_at = str(t_filter(self.delivered_at))
            if last_happen_at.date() != self.delivered_at.date():
                happen_at = str(d_filter(self.delivered_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLineType(
                happen_at=happen_at.title(),
                status=_('Delivered'),
                color='warning'
            ))

            last_happen_at = self.delivered_at

        for update_request in self.servicepurchaseupdaterequest_set \
                .order_by("created_at") \
                .all():
            happen_at = str(t_filter(update_request.created_at))
            if last_happen_at.date() != update_request.created_at.date():
                happen_at = str(d_filter(update_request.created_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLineType(
                happen_at=happen_at.title(),
                status=_('Request for update initiated'),
                color='dark',
                description=_('The buyer make an update request <strong>{}</strong>')
                    .format(update_request.title),
            ))

            last_happen_at = update_request.created_at

            if update_request.has_been_accepted:
                happen_at = str(t_filter(update_request.accepted_at))
                if last_happen_at.date() != update_request.accepted_at.date():
                    happen_at = str(d_filter(update_request.accepted_at)) + " " + happen_at

                timelines.append(ServicePurchaseTimeLineType(
                    happen_at=happen_at.title(),
                    status=_('Request for update accepted'),
                    color='primary',
                    description=_(
                        'The update request <strong>{}</strong> have been accepted. New deadline set to <strong>{}</strong>')
                        .format(update_request.title, date_filter(update_request.deadline_at)),
                ))

                last_happen_at = update_request.accepted_at

            if update_request.has_been_refused:
                happen_at = str(t_filter(update_request.refused_at))
                if last_happen_at.date() != update_request.refused_at.date():
                    happen_at = str(d_filter(update_request.refused_at)) + " " + happen_at

                timelines.append(ServicePurchaseTimeLineType(
                    happen_at=happen_at.title(),
                    status=_('Request for update refused'),
                    color='danger',
                    description=_(
                        'The update request <strong>{}</strong> have been refused. <strong>Reason:</strong> {}')
                        .format(update_request.title, update_request.reason),
                ))

                last_happen_at = update_request.refused_at

            if update_request.has_been_delivered:
                happen_at = str(t_filter(update_request.delivered_at))
                if last_happen_at.date() != update_request.delivered_at.date():
                    happen_at = str(d_filter(update_request.delivered_at)) + " " + happen_at

                timelines.append(ServicePurchaseTimeLineType(
                    happen_at=happen_at.title(),
                    status=_('Request for update delivered'),
                    color='warning',
                    description=_('The update request <strong>{}</strong> have been delivered.')
                        .format(update_request.title),
                ))

                last_happen_at = update_request.delivered_at

        if self.has_been_in_dispute:
            happen_at = str(t_filter(self.in_dispute_at))
            if last_happen_at.date() != self.in_dispute_at.date():
                happen_at = str(d_filter(self.in_dispute_at)) + " " + happen_at

            timelines.append(ServicePurchaseTimeLineType(
                happen_at=happen_at.title(),
                status=_('In dispute'),
                color='info',
                description=_('The buyer open a litigation <strong>{}</strong>')
                    .format(self.litigation.title),
            ))

            last_happen_at = self.in_dispute_at

            if self.has_been_canceled:
                happen_at = str(t_filter(self.canceled_at))
                if last_happen_at.date() != self.canceled_at.date():
                    happen_at = str(d_filter(self.canceled_at)) + " " + happen_at

                timelines.append(ServicePurchaseTimeLineType(
                    happen_at=happen_at.title(),
                    status=_('Canceled'),
                    color='danger',
                    description=_('Has been canceled by <strong>Administrators</strong>'),
                ))

            if self.has_been_approved:
                happen_at = str(t_filter(self.approved_at))
                if last_happen_at.date() != self.approved_at.date():
                    happen_at = str(d_filter(self.approved_at)) + " " + happen_at

                timelines.append(ServicePurchaseTimeLineType(
                    happen_at=happen_at.title(),
                    status=_('Approved'),
                    color='success',
                    description=_('Has been approved by <strong>Administrators</strong>'),
                ))

        if self.has_not_been_in_dispute:
            if self.has_been_canceled:
                happen_at = str(t_filter(self.canceled_at))
                if last_happen_at.date() != self.canceled_at.date():
                    happen_at = str(d_filter(self.canceled_at)) + " " + happen_at

                timelines.append(ServicePurchaseTimeLineType(
                    happen_at=happen_at.title(),
                    status=_('Canceled'),
                    color='danger',
                ))

            if self.has_been_approved:
                happen_at = str(t_filter(self.approved_at))
                if last_happen_at.date() != self.approved_at.date():
                    happen_at = str(d_filter(self.approved_at)) + " " + happen_at

                timelines.append(ServicePurchaseTimeLineType(
                    happen_at=happen_at.title(),
                    status=_('Approved'),
                    color='success'
                ))

        return timelines

    @account_required
    def resolve_chat(self, info):
        self: ServicePurchase

        messages = ChatMessage.objects \
            .annotate(marked=Case(When(chatmessagemarked__account=info.context.user.account, then=True),
                                  default=False,
                                  output_field=BooleanField())) \
            .filter(service_purchase=self) \
            .order_by('created_at')

        return get_chat_messages(messages, info.context.user.account)

    @account_required
    def resolve_chat_files(self, info):
        self: ServicePurchase

        messages = ChatMessage.objects \
            .annotate(marked=Case(When(chatmessagemarked__account=info.context.user.account, then=True),
                                  default=False,
                                  output_field=BooleanField())) \
            .filter(service_purchase=self, is_file=True) \
            .order_by('created_at')

        return get_chat_messages(messages, info.context.user.account)

    @account_required
    def resolve_chat_marked(self, info):
        self: ServicePurchase

        messages = ChatMessage.objects \
            .annotate(marked=Case(When(chatmessagemarked__account=info.context.user.account, then=True),
                                  default=False,
                                  output_field=BooleanField())) \
            .filter(service_purchase=self, chatmessagemarked__account=info.context.user.account) \
            .order_by('created_at')

        return get_chat_messages(messages, info.context.user.account)

    @admin_required
    def resolve_chat_history(self, info):
        self: ServicePurchase

        messages = ChatMessage.objects \
            .filter(service_purchase=self) \
            .prefetch_related("service_purchase") \
            .order_by('created_at')

        return get_chat_messages(messages)

    @admin_required
    def resolve_chat_files_history(self, info):
        self: ServicePurchase

        messages = ChatMessage.objects \
            .filter(service_purchase=self, is_file=True) \
            .prefetch_related("service_purchase") \
            .order_by('created_at')

        return get_chat_messages(messages)


def get_chat_messages(messages, account=None):
    chat_messages = []

    last_created_at = None
    for message in messages:
        message: ChatMessage

        chat_messages.append(message.display(account, last_created_at))

        last_created_at = message.created_at

    return chat_messages


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


class ChatMessageType(DjangoObjectType):
    display = graphene.Field(ServicePurchaseChatMessageType, required=True)

    class Meta:
        model = ChatMessage
        filter_fields = {
            "id": ("exact",),
        }

    @account_required
    def resolve_display(self, info):
        self: ChatMessage

        return self.display(info.context.user.account)


class LitigationType(DjangoObjectType):
    status = graphene.String(source="status_display", required=True)
    decision = graphene.String(source="decision_display")

    opened = graphene.Boolean(source="opened", required=True)
    handled = graphene.Boolean(source="handled", required=True)
    approved = graphene.Boolean(source="approved", required=True)
    canceled = graphene.Boolean(source="canceled", required=True)
    can_be_handled = graphene.Boolean(source="can_be_handled", required=True)

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


class StatsType(ObjectType):
    services_count = graphene.String(required=True)
    services_accepted_count = graphene.String(required=True)
    disputes_count = graphene.String(required=True)
    disputes_not_handled_count = graphene.String(required=True)
    refunds_count = graphene.String(required=True)
    refunds_not_processed_count = graphene.String(required=True)
    service_purchases_count = graphene.String(required=True)
    service_purchases_not_approved_count = graphene.String(required=True)
    accounts_count = graphene.String(required=True)
    commissions_sum = graphene.String(required=True)
