import os
import uuid

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Count
from django.http import JsonResponse
from django.template.defaultfilters import date
from django.template.defaultfilters import date as date_filter
from django.views import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from rest_framework import serializers

from rwanda.account.models import Deposit, Refund
from rwanda.administration.models import Parameter
from rwanda.purchase.models import ServicePurchase, Deliverable, DeliverableFile
from rwanda.service.models import Service


class DepositsDatatableView(BaseDatatableView):
    currency = Parameter.objects.get(label=Parameter.CURRENCY).value
    columns = [
        'amount',
        'created_at',
    ]

    def render_column(self, row, column):
        row: Deposit

        if column == "amount":
            return intcomma(row.amount) + " " + self.currency
        elif column == "created_at":
            return date(row.created_at)
        else:
            return super(DepositsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Deposit.objects.filter(account__user=self.request.user)


class RefundsDatatableView(BaseDatatableView):
    currency = Parameter.objects.get(label=Parameter.CURRENCY).value
    columns = [
        'amount',
        'phone_number',
        'created_at',
    ]

    def render_column(self, row, column):
        row: Refund

        if column == "amount":
            return intcomma(row.amount) + " " + self.currency
        elif column == "created_at":
            return date(row.created_at)
        else:
            return super(RefundsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Refund.objects.filter(account__user=self.request.user)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ServicesDatatableView(BaseDatatableView):
    columns = [
        'title',
        'delay',
        'activated',
        'published',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: Service

        if column == "created_at":
            return date_filter(row.created_at)
        elif column == "delay":
            return row.delay_display
        elif column == "activated":
            class_name = 'warning'
            if row.activated:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.activated_display)
        elif column == "published":
            class_name = 'warning'
            if row.published:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.published_display)
        elif column == "data":
            return ServiceSerializer(row).data
        else:
            return super(ServicesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Service.objects.filter(account__user=self.request.user)


class ServicePurchaseBaseSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField()
    number = serializers.CharField()

    class Meta:
        model = ServicePurchase
        fields = "__all__"


class ServicePurchaseSerializer(ServicePurchaseBaseSerializer):
    can_be_approved = serializers.BooleanField()
    can_be_canceled = serializers.BooleanField()
    can_be_in_dispute = serializers.BooleanField()


class ServicePurchasesDatatableView(BaseDatatableView):
    serializer = ServicePurchaseSerializer
    currency = Parameter.objects.get(label=Parameter.CURRENCY).value
    columns = [
        'service',
        'status',
        'delay',
        'price',
        'must_be_delivered_at',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: ServicePurchase

        if column == "service":
            return row.service.title
        elif column == "status":
            class_name = 'dark'
            if row.accepted:
                class_name = 'primary'

            if row.delivered:
                class_name = 'warning'

            if row.approved:
                class_name = 'success'

            if row.canceled:
                class_name = 'danger'

            if row.in_dispute:
                class_name = 'info'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.status_display)
        elif column == "delay":
            return row.delay_display
        elif column == "price":
            return row.price_display + " " + self.currency
        elif column == "created_at":
            return date_filter(row.created_at)
        elif column == "must_be_delivered_at":
            return date_filter(row.must_be_delivered_at)
        elif column == "data":
            return self.serializer(row).data
        else:
            return super(ServicePurchasesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return ServicePurchase.objects.prefetch_related("service").filter(account__user=self.request.user)


class ServiceOrderSerializer(ServicePurchaseBaseSerializer):
    can_be_accepted = serializers.BooleanField()
    can_be_delivered = serializers.BooleanField()


class ServiceOrdersDatatableView(ServicePurchasesDatatableView):
    serializer = ServiceOrderSerializer

    def get_initial_queryset(self):
        return ServicePurchase.objects.prefetch_related("service").filter(service__account__user=self.request.user)


class DeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverable
        fields = "__all__"


class OrderDeliverablesDatatableView(BaseDatatableView):
    columns = [
        'title',
        'version',
        'file_counts',
        'published',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: Deliverable

        if column == "created_at":
            return date_filter(row.created_at)
        elif column == "file_counts":
            return intcomma(row.file_counts)
        elif column == "version":
            class_name = 'success'
            if row.alpha:
                class_name = 'primary'

            if row.beta:
                class_name = 'warning'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.version_display)
        elif column == "published":
            class_name = 'warning'
            if row.published:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.published_display)
        elif column == "data":
            return DeliverableSerializer(row).data
        else:
            return super(OrderDeliverablesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Deliverable.objects.annotate(file_counts=Count('deliverablefile')) \
            .filter(service_purchase=self.kwargs['pk'])


class DeliverableUploadView(View):
    def post(self, request, *args, **kwargs):
        f: UploadedFile = request.FILES['file']
        if f is not None:
            file_name = uuid.uuid4().urn[9:] + '.' + f.name.split('.')[-1]
            folder = "deliverables"
            file_path = os.path.join(settings.BASE_DIR, "media", folder, file_name)

            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            deliverable_file = DeliverableFile()
            deliverable_file.deliverable_id = kwargs['pk']
            deliverable_file.name = f.name
            deliverable_file.file = folder + "/" + file_name
            deliverable_file.save()
        return JsonResponse("True", safe=False)
