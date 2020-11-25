import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import date as date_filter, time as time_filter
from django.utils import timezone


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_online = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    image = models.FileField(blank=True, null=True, upload_to="accounts/")
    created_at = models.DateTimeField(auto_now_add=True)

    def disconnect(self):
        self.is_online = False
        self.last_login = timezone.now()
        self.save()

    @property
    def last_login_display(self):
        if self.last_login is not None:
            today = timezone.now()
            yesterday = timezone.now() - timedelta(1)

            d_filter = date_filter
            t_filter = time_filter
            if self.last_login.date() == today.date() or self.last_login.date() == yesterday.date():
                d_filter = naturalday

            return d_filter(self.last_login).title() + " " + t_filter(self.last_login)

        return None

    @property
    def is_account(self):
        try:
            return self.account is not None
        except Exception:
            return False

    @property
    def is_not_account(self):
        return not self.is_account

    @property
    def is_admin(self):
        try:
            return self.admin is not None
        except Exception:
            return False

    @property
    def is_not_admin(self):
        return not self.is_admin

    @property
    def image_url(self):
        try:
            return settings.BASE_URL + self.image.url
        except Exception:
            return None


class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name="admin", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    balance = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    @property
    def created_at_display(self):
        return date_filter(self.created_at) + ' ' + time_filter(self.created_at)

    @property
    def balance_display(self):
        return intcomma(self.balance)

    @property
    def services_count(self):
        from rwanda.service.models import Service
        return Service.objects.filter(account=self).count()

    @property
    def services_count_display(self):
        return intcomma(self.services_count)

    @property
    def purchases_count(self):
        from rwanda.purchase.models import ServicePurchase
        return ServicePurchase.objects.filter(account=self).count()

    @property
    def purchases_count_display(self):
        return intcomma(self.purchases_count)

    @property
    def orders_count(self):
        from rwanda.purchase.models import ServicePurchase
        return ServicePurchase.objects.filter(service__account=self).count()

    @property
    def orders_count_display(self):
        return intcomma(self.orders_count)

    @property
    def deposits_sum(self):
        from rwanda.account.models import Deposit
        deposits_sum = Deposit.objects.filter(account=self).aggregate(Sum('amount'))['amount__sum']
        if deposits_sum is None:
            deposits_sum = 0
        return deposits_sum

    @property
    def deposits_sum_display(self):
        return intcomma(self.deposits_sum)

    @property
    def refunds_sum(self):
        from rwanda.account.models import Refund
        refunds_sum = Refund.objects.filter(account=self).aggregate(Sum('amount'))['amount__sum']
        if refunds_sum is None:
            refunds_sum = 0
        return refunds_sum

    @property
    def refunds_sum_display(self):
        return intcomma(self.refunds_sum)

    @property
    def earnings_sum(self):
        from rwanda.accounting.models import Operation
        earnings_sum = Operation.objects.filter(account=self, description=Operation.DESC_CREDIT_FOR_PURCHASE_APPROVED) \
            .aggregate(Sum('amount'))['amount__sum']
        if earnings_sum is None:
            earnings_sum = 0
        return earnings_sum

    @property
    def earnings_sum_display(self):
        return intcomma(self.earnings_sum)
