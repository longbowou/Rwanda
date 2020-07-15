import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
# PARAMETRES
class Parameters(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.label

# LES DIFFERENTS COMPTES
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


# LES AUTRES TABLES
class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.label


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    content = models.TextField
    keywords = models.TextField(blank=True, null=True)
    stars = models.IntegerField(default=0)
    delay = models.IntegerField
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ServiceMedias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class Comments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField
    positive = models.BooleanField
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class ServiceOptions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    delay = models.IntegerField
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    def __str__(self):
        return self.label


class SellerPurchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delay = models.IntegerField
    accepted = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class SellerPurchaseServiceOptions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_options = models.ForeignKey(ServiceOptions, on_delete=models.CASCADE)
    seller_purchase = models.ForeignKey(SellerPurchase, on_delete=models.CASCADE)


class Chats(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField
    seller_purchase = models.ForeignKey(SellerPurchase, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Litigation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField
    handled = models.BooleanField(default=False)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    seller_purchase = models.ForeignKey(SellerPurchase, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
