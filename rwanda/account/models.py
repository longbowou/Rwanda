import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from rwanda.payments.models import Payment
from rwanda.user.models import Account


class Deposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.PositiveBigIntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
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
    status = models.CharField(max_length=255, default=STATUS_INITIATED)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
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
    def in_progress(self):
        return self.status == self.STATUS_IN_PROGRESS

    @property
    def status_display(self):
        if self.processed:
            return _('Processed')

        if self.in_progress:
            return _('In Progress')

        return _("Initiated")

    def __str__(self):
        return self.amount

    @property
    def can_be_processed(self):
        return self.initiated

    def set_as_in_progress(self):
        self.status = self.STATUS_IN_PROGRESS
