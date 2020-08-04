import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from rwanda.service.models import Service, ServiceOption
from rwanda.user.models import Admin, Account


class Parameter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label

    BASE_PRICE = "BASE_PRICE"
    CURRENCY = "CURRENCY"
    COMMISSION = "COMMISSION"
