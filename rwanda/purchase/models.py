import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.template.defaultfilters import date as date_filter, time as time_filter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rwanda.account.utils import natural_size
from rwanda.administration.models import Parameter
from rwanda.administration.utils import param_service_purchase_cancellation_delay
from rwanda.service.models import Service, ServiceOption
from rwanda.user.models import Account, Admin


class ServicePurchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delay = models.PositiveBigIntegerField()
    price = models.PositiveBigIntegerField()
    commission = models.PositiveBigIntegerField()
    STATUS_INITIATED = 'INITIATED'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REFUSED = 'REFUSED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELED = 'CANCELED'
    STATUS_IN_DISPUTE = 'IN_DISPUTE'
    STATUS_UPDATE_INITIATED = 'UPDATE_INITIATED'
    STATUS_UPDATE_ACCEPTED = 'UPDATE_ACCEPTED'
    STATUS_UPDATE_REFUSED = 'UPDATE_REFUSED'
    STATUS_UPDATE_DELIVERED = 'UPDATE_DELIVERED'
    status = models.CharField(max_length=255, default=STATUS_INITIATED)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_options = models.ManyToManyField(ServiceOption, blank=True,
                                             through='ServicePurchaseServiceOption')
    accepted_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    in_dispute_at = models.DateTimeField(null=True, blank=True)
    deadline_at = models.DateTimeField(null=True, blank=True)
    has_final_deliverable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def number(self):
        return "#" + str(self.id)[24:].upper()

    @property
    def deadline_at_display(self):
        if self.has_not_been_accepted:
            return None

        return date_filter(self.deadline_at)

    @property
    def service_title(self):
        return self.service.title

    @property
    def price_display(self):
        return intcomma(self.price)

    @property
    def delay_display(self):
        return str(self.delay) + " total delivery {}".format(_('days'))

    @property
    def status_display(self):
        if self.accepted:
            return _('Accepted')

        if self.delivered:
            return _('Delivered')

        if self.approved:
            return _('Approved')

        if self.canceled:
            return _('Canceled')

        if self.update_initiated:
            return _('Update request initiated')

        if self.update_accepted:
            return _('Update request accepted')

        if self.update_refused:
            return _('Update request refused')

        if self.update_delivered:
            return _('Update request delivered')

        return _("Initiated")

    @property
    def total_price(self):
        return self.price + self.commission

    @property
    def initiated(self):
        return self.status == self.STATUS_INITIATED

    @property
    def accepted(self):
        return self.status == self.STATUS_ACCEPTED

    @property
    def refused(self):
        return self.status == self.STATUS_REFUSED

    @property
    def delivered(self):
        return self.status == self.STATUS_DELIVERED

    @property
    def approved(self):
        return self.status == self.STATUS_APPROVED

    @property
    def canceled(self):
        return self.status == self.STATUS_CANCELED

    @property
    def update_initiated(self):
        return self.status == self.STATUS_UPDATE_INITIATED

    @property
    def update_accepted(self):
        return self.status == self.STATUS_UPDATE_ACCEPTED

    @property
    def update_refused(self):
        return self.status == self.STATUS_UPDATE_REFUSED

    @property
    def update_delivered(self):
        return self.status == self.STATUS_UPDATE_DELIVERED

    @property
    def in_dispute(self):
        return self.status == self.STATUS_IN_DISPUTE

    @property
    def has_been_accepted(self):
        return self.accepted_at is not None

    @property
    def has_not_been_accepted(self):
        return not self.has_been_accepted

    @property
    def has_been_delivered(self):
        return self.delivered_at is not None

    @property
    def has_been_approved(self):
        return self.approved_at is not None

    @property
    def has_been_canceled(self):
        return self.canceled_at is not None

    @property
    def has_been_in_dispute(self):
        return self.in_dispute_at is not None

    @property
    def has_not_been_in_dispute(self):
        return not self.has_been_in_dispute

    @property
    def can_add_deliverable(self):
        return self.accepted or self.delivered

    @property
    def can_be_accepted(self):
        return self.initiated

    @property
    def cannot_be_accepted(self):
        return not self.can_be_accepted

    @property
    def can_be_delivered(self):
        return self.accepted and self.has_final_deliverable

    @property
    def cannot_be_delivered(self):
        return not self.can_be_delivered

    @property
    def can_be_approved(self):
        return self.delivered or self.update_delivered or self.update_refused

    @property
    def cannot_be_approved(self):
        return not self.can_be_approved

    @property
    def can_be_canceled(self):
        if self.initiated:
            return True

        if self.canceled:
            return False

        return self.can_be_canceled_for_delay

    @property
    def cannot_be_canceled(self):
        return not self.can_be_canceled

    @property
    def can_be_in_dispute(self):
        return self.delivered

    @property
    def cannot_be_in_dispute(self):
        return not self.can_be_in_dispute

    @property
    def can_ask_for_update(self):
        return self.delivered or self.update_delivered or self.update_refused

    @property
    def cannot_ask_for_update(self):
        return not self.can_ask_for_update

    @property
    def can_be_canceled_for_delay(self):
        in_between_days = (timezone.now() - self.deadline_at).days
        cancellation_delay_days = int(param_service_purchase_cancellation_delay())
        return not self.approved and in_between_days > cancellation_delay_days

    @property
    def canceled_for_delay(self):
        return self.accepted and self.canceled and self.canceled_at > self.deadline_at

    def set_as_accepted(self):
        self.status = self.STATUS_ACCEPTED
        today = timezone.now()
        self.accepted_at = today
        self.deadline_at = today + timedelta(days=self.delay)

    def set_as_delivered(self):
        self.status = self.STATUS_DELIVERED
        self.delivered_at = timezone.now()

    def set_as_approved(self):
        self.status = self.STATUS_APPROVED
        self.approved_at = timezone.now()

    def set_as_canceled(self):
        self.status = self.STATUS_CANCELED
        self.canceled_at = timezone.now()

    def set_in_dispute(self):
        self.status = self.STATUS_IN_DISPUTE
        self.in_dispute_at = timezone.now()

    def set_as_update_initiated(self):
        self.status = self.STATUS_UPDATE_INITIATED

    def set_as_update_accepted(self):
        self.deadline_at = timezone.now() + timedelta(days=self.delay)
        self.status = self.STATUS_UPDATE_ACCEPTED

    def set_as_update_refused(self):
        self.status = self.STATUS_UPDATE_REFUSED

    def set_as_update_delivered(self):
        self.status = self.STATUS_UPDATE_DELIVERED

    def is_buyer(self, account: Account):
        return self.account_id == account.id

    def is_not_buyer(self, account: Account):
        return not self.is_buyer(account)

    def is_seller(self, account: Account):
        return self.service.account_id == account.id

    def is_not_seller(self, account: Account):
        return not self.is_seller(account)


class ServicePurchaseUpdateRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    STATUS_INITIATED = "INITIATED"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_REFUSED = "REFUSED"
    STATUS_DELIVERED = "DELIVERED"
    status = models.CharField(max_length=255, default=STATUS_INITIATED)
    accepted_at = models.DateTimeField(null=True, blank=True)
    refused_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    deadline_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    service_purchase = models.ForeignKey(ServicePurchase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def deadline_at_display(self):
        if not self.has_been_accepted:
            return None

        return date_filter(self.deadline_at)

    @property
    def status_display(self):
        if self.accepted:
            return _('Accepted')

        if self.refused:
            return _('Refused')

        if self.delivered:
            return _('Delivered')

        return _("Initiated")

    @property
    def initiated(self):
        return self.status == self.STATUS_INITIATED

    @property
    def accepted(self):
        return self.status == self.STATUS_ACCEPTED

    @property
    def refused(self):
        return self.status == self.STATUS_REFUSED

    @property
    def delivered(self):
        return self.status == self.STATUS_DELIVERED

    @property
    def can_be_accepted(self):
        return self.initiated

    @property
    def cannot_be_accepted(self):
        return not self.can_be_accepted

    @property
    def can_be_refused(self):
        return self.initiated

    @property
    def cannot_be_refused(self):
        return not self.can_be_refused

    @property
    def can_be_delivered(self):
        return self.accepted

    @property
    def cannot_be_delivered(self):
        return not self.can_be_delivered

    @property
    def has_been_accepted(self):
        return self.accepted_at is not None

    @property
    def has_been_refused(self):
        return self.refused_at is not None

    @property
    def has_been_delivered(self):
        return self.delivered_at is not None

    def set_as_accepted(self):
        self.status = self.STATUS_ACCEPTED
        self.accepted_at = timezone.now()

    def set_as_refused(self):
        self.status = self.STATUS_REFUSED
        self.refused_at = timezone.now()

    def set_as_delivered(self):
        self.status = self.STATUS_DELIVERED
        self.delivered_at = timezone.now()


class ServicePurchaseServiceOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_option = models.ForeignKey(ServiceOption, on_delete=models.CASCADE)
    service_purchase = models.ForeignKey(ServicePurchase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(null=True, blank=True)
    is_file = models.BooleanField(default=False)
    file = models.FileField(upload_to="chat_files/", null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    file_size = models.BigIntegerField(default=0)
    service_purchase = models.ForeignKey(ServicePurchase, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def file_size_display(self):
        if self.is_file:
            return natural_size(self.file_size)

    def display(self, account, last_created_at=None):
        from rwanda.graphql.types import ServicePurchaseChatMessageType

        today = timezone.now()
        yesterday = timezone.now() - timedelta(1)

        d_filter = date_filter
        t_filter = time_filter
        if self.created_at.date() == today.date() or self.created_at.date() == yesterday.date():
            d_filter = naturalday

        chat_message = ServicePurchaseChatMessageType()
        chat_message.id = self.id
        chat_message.content = self.content
        chat_message.marked = getattr(self, "marked", False)
        chat_message.time = t_filter(self.created_at).title()
        chat_message.date = int(self.created_at.strftime("%Y%m%d"))
        chat_message.date_display = d_filter(self.created_at).title()
        chat_message.created_at = self.created_at.timestamp()

        chat_message.is_file = self.is_file
        if self.is_file:
            chat_message.file_name = self.file_name
            chat_message.file_size = self.file_size_display
            chat_message.file_url = settings.BASE_URL + self.file.url

        chat_message.from_current_account = False
        if self.account_id == account.id:
            chat_message.from_current_account = True

        chat_message.show_date = False
        if last_created_at is None or last_created_at is not None and last_created_at.date() != self.created_at.date():
            chat_message.show_date = True

        return chat_message


class ChatMessageMarked(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Litigation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    DECISION_APPROVED = 'APPROVED'
    DECISION_CANCELED = 'CANCELED'
    decisions = (
        (DECISION_APPROVED, DECISION_APPROVED),
        (DECISION_CANCELED, DECISION_CANCELED),
    )
    decision = models.CharField(max_length=255, choices=decisions, blank=True, null=True)
    handled = models.BooleanField(default=False)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, blank=True, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    service_purchase = models.OneToOneField(ServicePurchase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def approved(self):
        return self.decision == self.DECISION_APPROVED

    @property
    def canceled(self):
        return self.decision == self.DECISION_CANCELED


class Deliverable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    VERSION_ALPHA = 'ALPHA'
    VERSION_BETA = 'BETA'
    VERSION_FINAL = 'FINAL'
    version = models.CharField(max_length=255)
    description = models.TextField()
    published = models.BooleanField(default=False)
    service_purchase = models.ForeignKey(ServicePurchase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deliverable_files_count = None

    def __str__(self):
        return self.title

    @property
    def alpha(self):
        return self.version == self.VERSION_ALPHA

    @property
    def files_count(self):
        if self.deliverable_files_count is None:
            self.deliverable_files_count = DeliverableFile.objects.filter(deliverable=self).count()
        return self.deliverable_files_count

    @property
    def files_count_display(self):
        return intcomma(self.files_count)

    @property
    def beta(self):
        return self.version == self.VERSION_BETA

    @property
    def final(self):
        return self.version == self.VERSION_FINAL

    @property
    def version_display(self):
        if self.alpha:
            return _('Alpha')

        if self.beta:
            return _('Beta')

        return _('Final')

    @property
    def published_display(self):
        if self.published:
            return _('Yes')

        return _('No')


class DeliverableFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='deliverables/')
    size = models.BigIntegerField(default=0)
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def size_display(self):
        return natural_size(self.size)
