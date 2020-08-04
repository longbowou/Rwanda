import uuid

from django.db import models

from rwanda.purchase.models import ServicePurchase
from rwanda.user.models import Account


class Fund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=100, unique=True)
    balance = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    MAIN = "MAIN"
    COMMISSIONS = "COMMISSIONS"
    ACCOUNTS = "ACCOUNTS"

    def __str__(self):
        return self.label


class Operation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100)
    amount = models.BigIntegerField()
    description = models.TextField(null=True, blank=True)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    service_purchase = models.ForeignKey(ServicePurchase, null=True, blank=True, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

    def __str__(self):
        return self.type
