import uuid

from django.db import models

from rwanda.service.models import Service, ServiceOption
from rwanda.user.models import Account, Admin


class ServicePurchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delay = models.IntegerField()
    price = models.IntegerField()
    commission = models.IntegerField()
    accepted = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
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
    def fees(self):
        return self.price - self.commission


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
    handled = models.BooleanField(default=False)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    service_purchase = models.OneToOneField(ServicePurchase, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
