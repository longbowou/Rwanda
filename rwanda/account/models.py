import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from rwanda.payments.models import Payment
from rwanda.user.models import Account


class Deposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.PositiveBigIntegerField()
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.amount


class RefundWay(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    country_code = models.CharField(max_length=255)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def published_display(self):
        if self.published:
            return _('Yes')

        return _('No')


class Refund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.PositiveBigIntegerField()
    STATUS_INITIATED = "INITIATED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_PROCESSED = "PROCESSED"
    STATUS_CANCELED = "CANCELED"
    status = models.CharField(max_length=255, default=STATUS_INITIATED)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    canceled_reason = models.TextField(null=True, blank=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    refund_way = models.ForeignKey(RefundWay, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.amount

    @property
    def initiated(self):
        return self.status == self.STATUS_INITIATED

    @property
    def processed(self):
        return self.status == self.STATUS_PROCESSED

    @property
    def canceled(self):
        return self.status == self.STATUS_CANCELED

    @property
    def in_progress(self):
        return self.status == self.STATUS_IN_PROGRESS

    @property
    def status_display(self):
        if self.processed:
            return _('Processed')

        if self.in_progress:
            return _('In Progress')

        return _("Initiated")

    @property
    def can_be_processed(self):
        return self.initiated

    @property
    def can_be_canceled(self):
        return self.initiated or self.in_progress

    def set_as_in_progress(self):
        self.status = self.STATUS_IN_PROGRESS

    def set_as_processed(self):
        self.status = self.STATUS_PROCESSED

    def set_as_canceled(self, canceled_reason):
        self.canceled_reason = canceled_reason
        self.status = self.STATUS_CANCELED
