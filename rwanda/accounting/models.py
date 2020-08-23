import uuid

from django.db import models

from rwanda.purchase.models import ServicePurchase
from rwanda.user.models import Account


class Fund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, unique=True)
    balance = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    MAIN = "MAIN"
    COMMISSIONS = "COMMISSIONS"
    ACCOUNTS = "ACCOUNTS"

    def __str__(self):
        return self.label


class Operation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=255)
    amount = models.PositiveBigIntegerField()
    description = models.TextField(null=True, blank=True)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)
    service_purchase = models.ForeignKey(ServicePurchase, null=True, blank=True, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    TYPE_CREDIT = "CREDIT"
    TYPE_DEBIT = "DEBIT"

    DESC_DEBIT_FOR_PURCHASE_INIT = "DEBIT_FOR_PURCHASE_INIT"
    DESC_CREDIT_FOR_PURCHASE_INIT = "CREDIT_FOR_PURCHASE_INIT"

    DESC_DEBIT_FOR_PURCHASE_APPROVED = "DEBIT_FOR_PURCHASE_APPROVED"
    DESC_CREDIT_FOR_PURCHASE_APPROVED = "CREDIT_FOR_PURCHASE_APPROVED"

    DESC_DEBIT_FOR_PURCHASE_CANCELED = "DEBIT_FOR_PURCHASE_CANCELED"
    DESC_CREDIT_FOR_PURCHASE_CANCELED = "CREDIT_FOR_PURCHASE_CANCELED"

    DESC_CREDIT_FOR_DEPOSIT = "CREDIT_FOR_DEPOSIT"
    DESC_DEBIT_FOR_REFUND = "DEBIT_FOR_REFUND"

    def __str__(self):
        return self.type
