import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.template.defaultfilters import date as date_filter, time as time_filter
from django.utils.translation import gettext_lazy as _

from rwanda.user.models import Account


class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.TextField(blank=True, null=True)
    STATUS_SUBMITTED_FOR_APPROVAL = 'SUBMITTED_FOR_APPROVAL'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REJECTED = 'REJECTED'
    status = models.CharField(max_length=255, default=STATUS_SUBMITTED_FOR_APPROVAL)
    rejected_reason = models.TextField(blank=True, null=True)
    stars = models.IntegerField(default=0)
    delay = models.PositiveBigIntegerField(default=0)
    file = models.FileField(blank=True, null=True, upload_to="services/")
    published = models.BooleanField(default=False)
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    service_options_count = None

    def __str__(self):
        return self.title

    def is_owner(self, account):
        return self.account_id == account.id

    def is_not_owner(self, account):
        return not self.is_owner(account)

    @property
    def accepted(self):
        return self.status == self.STATUS_ACCEPTED

    @property
    def rejected(self):
        return self.status == self.STATUS_REJECTED

    @property
    def submitted_for_approval(self):
        return self.status == self.STATUS_SUBMITTED_FOR_APPROVAL

    @property
    def can_be_accepted(self):
        return self.submitted_for_approval

    @property
    def cannot_be_accepted(self):
        return not self.can_be_accepted

    @property
    def can_be_rejected(self):
        return self.submitted_for_approval

    @property
    def cannot_be_rejected(self):
        return not self.can_be_rejected

    @property
    def can_be_submitted_for_approval(self):
        return self.rejected

    @property
    def cannot_be_submitted_for_approval(self):
        return not self.can_be_submitted_for_approval

    @property
    def status_display(self):
        if self.accepted:
            return _('Accepted')

        if self.rejected:
            return _('Rejected')

        return _('Submitted for approval')

    @property
    def delay_display(self):
        return str(self.delay) + " " + str(_("delivery days"))

    @property
    def file_url(self):
        try:
            return settings.BASE_URL + self.file.url
        except Exception:
            return None

    @property
    def options_count(self):
        if self.service_options_count is None:
            self.service_options_count = ServiceOption.objects.filter(service=self).count()
        return self.service_options_count

    @property
    def options_count_display(self):
        return intcomma(self.options_count)

    @property
    def created_at_display(self):
        return date_filter(self.created_at) + ' ' + time_filter(self.created_at)

    @property
    def published_display(self):
        if self.published:
            return _('Yes')

        return _('No')

    def set_as_rejected(self):
        self.status = self.STATUS_REJECTED

    def set_as_accepted(self):
        self.status = self.STATUS_ACCEPTED
        self.accepted_at = datetime.today()

    def set_as_submitted_for_approval(self):
        self.status = self.STATUS_SUBMITTED_FOR_APPROVAL


class ServiceMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to="service-medias/")
    is_main = models.BooleanField(default=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def file_url(self):
        return settings.BASE_URL + self.file.url if self.file else None


class ServiceComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    reply_content = models.TextField(blank=True, null=True)
    TYPE_POSITIVE = 'POSITIVE'
    TYPE_NEGATIVE = 'NEGATIVE'
    type = models.CharField(max_length=255, blank=True, null=True)
    service_purchase = models.ForeignKey("purchase.ServicePurchase", on_delete=models.CASCADE, blank=True, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    reply_at = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def created_at_display(self):
        return date_filter(self.created_at) + ' ' + time_filter(self.created_at)

    @property
    def positive(self):
        return self.type == self.TYPE_POSITIVE

    @property
    def negative(self):
        return self.type == self.TYPE_NEGATIVE


class ServiceOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    delay = models.PositiveBigIntegerField()
    price = models.PositiveBigIntegerField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label

    @property
    def published_display(self):
        if self.published:
            return _('Yes')

        return _('No')

    @property
    def price_display(self):
        return intcomma(self.price)

    @property
    def delay_display(self):
        if self.delay == 0:
            return _("No additional delivery delay")
        return str(self.delay) + " " + str(_('delivery days'))

    @property
    def delay_preview_display(self):
        if self.delay == 0:
            return _("No additional delivery delay")
        return _("{} additional delivery days").format(str(self.delay))
