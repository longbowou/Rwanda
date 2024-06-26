import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from rwanda.users.models import Account


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.PositiveBigIntegerField()
    fee = models.PositiveBigIntegerField(default=0)
    TYPE_INCOMING = 'INCOMING'
    TYPE_OUTGOING = 'OUTGOING'
    type = models.CharField(max_length=255, default=TYPE_INCOMING)
    STATUS_INITIATED = 'INITIATED'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELED = 'CANCELED'
    status = models.CharField(max_length=255, default=STATUS_INITIATED)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    signature = models.TextField(null=True, blank=True)
    cpm_payid = models.TextField(null=True, blank=True)
    payment_method = models.TextField(null=True, blank=True)
    cpm_phone_prefixe = models.TextField(null=True, blank=True)
    cel_phone_num = models.TextField(null=True, blank=True)
    cpm_result = models.TextField(null=True, blank=True)
    cpm_trans_status = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return self.amount + self.fee

    @property
    def status_display(self):
        if self.confirmed:
            return _('Confirmed')

        if self.canceled:
            return _('Canceled')

        return _("Initiated")

    @property
    def initiated(self):
        return self.status == self.STATUS_INITIATED

    @property
    def confirmed(self):
        return self.status == self.STATUS_CONFIRMED

    @property
    def canceled(self):
        return self.status == self.STATUS_CANCELED

    @property
    def incoming(self):
        return self.type == self.TYPE_INCOMING

    @property
    def outgoing(self):
        return self.type == self.TYPE_OUTGOING

    def set_as_confirmed(self):
        self.status = self.STATUS_CONFIRMED

    def set_as_canceled(self):
        self.status = self.STATUS_CANCELED
