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


class Refund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.PositiveBigIntegerField()
    STATUS_INITIATED = "INITIATED"
    STATUS_APPROVED = "APPROVED"
    status = models.CharField(max_length=255, default=STATUS_INITIATED)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    refund_way = models.ForeignKey(RefundWay, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def initiated(self):
        return self.status == self.STATUS_INITIATED

    @property
    def approved(self):
        return self.status == self.STATUS_APPROVED

    @property
    def status_display(self):
        if self.approved:
            return _('Approved')

        return _("Initiated")

    def __str__(self):
        return self.amount
