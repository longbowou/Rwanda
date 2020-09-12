import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.db.models import Sum


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_account(self):
        try:
            return self.account is not None
        except Exception:
            return False

    @property
    def is_not_account(self):
        return not self.is_account


class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name="admin", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    balance = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    @property
    def services_count(self):
        from rwanda.service.models import Service
        return intcomma(Service.objects.filter(account=self).count())

    @property
    def purchases_count(self):
        from rwanda.purchase.models import ServicePurchase
        return intcomma(ServicePurchase.objects.filter(account=self).count())

    @property
    def deposits_sum(self):
        from rwanda.account.models import Deposit
        deposits_sum = Deposit.objects.filter(account=self).aggregate(Sum('amount'))['amount__sum']
        if deposits_sum is None:
            deposits_sum = 0
        return intcomma(deposits_sum)

    @property
    def refunds_sum(self):
        from rwanda.account.models import Refund
        refunds_sum = Refund.objects.filter(account=self).aggregate(Sum('amount'))['amount__sum']
        if refunds_sum is None:
            refunds_sum = 0
        return intcomma(refunds_sum)

    @property
    def earnings_sum(self):
        from rwanda.accounting.models import Operation
        earnings_sum = Operation.objects.filter(account=self, description=Operation.DESC_CREDIT_FOR_PURCHASE_APPROVED) \
            .aggregate(Sum('amount'))['amount__sum']
        if earnings_sum is None:
            earnings_sum = 0
        return intcomma(earnings_sum)
