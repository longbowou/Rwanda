import uuid

from django.db import models


class Parameter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label

    BASE_PRICE = "BASE_PRICE"
    CURRENCY = "CURRENCY"
    COMMISSION = "COMMISSION"
    CINETPAY_PASSWORD = "CINETPAY_PASSWORD"
