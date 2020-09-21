import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from rwanda.user.models import Account


class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.TextField(blank=True, null=True)
    stars = models.IntegerField(default=0)
    delay = models.PositiveBigIntegerField(default=0)
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    activated = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def not_activated(self):
        return not self.activated

    @property
    def activated_display(self):
        if self.activated:
            return _('Yes')

        return _('No')

    @property
    def published_display(self):
        if self.published:
            return _('Yes')

        return _('No')


class ServiceMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to="service-medias/")
    is_main = models.BooleanField(default=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def file_url(self):
        return self.file.url if self.file else None


class ServiceComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    reply_content = models.TextField(blank=True, null=True)
    positive = models.BooleanField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    reply_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServiceOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    delay = models.PositiveBigIntegerField()
    price = models.PositiveBigIntegerField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label

    @property
    def published_display(self):
        if self.published:
            return _('Yes')

        return _('No')

