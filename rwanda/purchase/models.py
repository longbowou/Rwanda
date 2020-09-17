import uuid
from datetime import timedelta

from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rwanda.administration.models import Parameter
from rwanda.service.models import Service, ServiceOption
from rwanda.user.models import Account, Admin


class ServicePurchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delay = models.PositiveBigIntegerField()
    price = models.PositiveBigIntegerField()
    commission = models.PositiveBigIntegerField()
    STATUS_INITIATED = 'INITIATED'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_APPROVED = 'APPROVED'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELED = 'CANCELED'
    status = models.CharField(max_length=255, default=STATUS_INITIATED)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    service_options = models.ManyToManyField(ServiceOption, blank=True,
                                             through='ServicePurchaseServiceOption')
    accepted_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    must_be_delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def service_title(self):
        return self.service.title

    @property
    def price_display(self):
        return intcomma(self.price)

    @property
    def delay_display(self):
        return str(self.delay) + " {}".format(_('Days'))

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
    def delivered(self):
        return self.status == self.STATUS_DELIVERED

    @property
    def approved(self):
        return self.status == self.STATUS_APPROVED

    @property
    def canceled(self):
        return self.status == self.STATUS_CANCELED

    @property
    def can_be_accepted(self):
        return self.initiated

    @property
    def cannot_be_accepted(self):
        return not self.can_be_accepted

    @property
    def can_be_delivered(self):
        return self.accepted

    @property
    def cannot_be_delivered(self):
        return not self.can_be_delivered

    @property
    def can_be_approved(self):
        return self.delivered

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
    def can_create_litigation(self):
        return self.delivered

    @property
    def cannot_create_litigation(self):
        return not self.can_create_litigation

    @property
    def can_be_canceled_for_delay(self):
        in_between_days = (timezone.now() - self.must_be_delivered_at).days
        cancellation_delay_days = int(Parameter.objects.get(label=Parameter.SERVICE_PURCHASE_CANCELLATION_DELAY).value)
        return not self.approved and in_between_days > cancellation_delay_days

    @property
    def canceled_for_delay(self):
        return self.accepted and self.canceled and self.canceled_at > self.must_be_delivered_at

    def set_as_accepted(self):
        self.status = self.STATUS_ACCEPTED
        today = timezone.now()
        self.accepted_at = today
        self.must_be_delivered_at = today + timedelta(days=self.delay)

    def set_as_delivered(self):
        self.status = self.STATUS_DELIVERED
        self.delivered_at = timezone.now()

    def set_as_approved(self):
        self.status = self.STATUS_APPROVED
        self.approved_at = timezone.now()

    def set_as_canceled(self):
        self.status = self.STATUS_CANCELED
        self.canceled_at = timezone.now()

    def is_buyer(self, account: Account):
        return self.account_id == account.id

    def is_not_buyer(self, account: Account):
        return not self.is_buyer(account)

    def is_seller(self, account: Account):
        return self.service.account_id == account.id

    def is_not_seller(self, account: Account):
        return not self.is_seller(account)


class ServicePurchaseServiceOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_option = models.ForeignKey(ServiceOption, on_delete=models.CASCADE)
    service_purchase = models.ForeignKey(ServicePurchase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    service_purchase = models.ForeignKey(ServicePurchase, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
