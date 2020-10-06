import os
import uuid

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Count
from django.http import JsonResponse
from django.template.defaultfilters import date
from django.template.defaultfilters import date as date_filter, time as time_filter
from django.views import View
from django_datatables_view.base_datatable_view import BaseDatatableView

from rwanda.account.models import Deposit, Refund
from rwanda.account.serializers import ServiceSerializer, PurchaseSerializer, OrderSerializer, \
    DeliverableSerializer, DeliverableFileSerializer, ServiceOptionsSerializer
from rwanda.account.utils import create_folder_if_not_exits
from rwanda.administration.utils import param_currency
from rwanda.graphql.purchase.subscriptions import ChatMessageSubscription
from rwanda.purchase.models import ServicePurchase, Deliverable, DeliverableFile, ChatMessage
from rwanda.service.models import Service, ServiceOption


class DepositsDatatableView(BaseDatatableView):
    currency = None
    columns = [
        'amount',
        'created_at',
    ]

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.currency = param_currency()

    def render_column(self, row, column):
        row: Deposit

        if column == "amount":
            return intcomma(row.amount) + " " + self.currency
        elif column == "created_at":
            return date(row.created_at) + ' ' + time_filter(row.created_at)
        else:
            return super(DepositsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Deposit.objects.filter(account__user=self.request.user)


class RefundsDatatableView(BaseDatatableView):
    currency = None
    columns = [
        'amount',
        'phone_number',
        'created_at',
    ]

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.currency = param_currency()

    def render_column(self, row, column):
        row: Refund

        if column == "amount":
            return intcomma(row.amount) + " " + self.currency
        elif column == "created_at":
            return date(row.created_at) + ' ' + time_filter(row.created_at)
        else:
            return super(RefundsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Refund.objects.filter(account__user=self.request.user)


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
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
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


class PurchasesDatatableView(BaseDatatableView):
    serializer = PurchaseSerializer
    currency = None
    columns = [
        'number',
        'service',
        'status',
        'delay',
        'price',
        'deadline_at',
        'created_at',
        'data'
    ]

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.currency = param_currency()

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
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
        elif column == "deadline_at":
            return date_filter(row.deadline_at)
        elif column in ["data", 'number']:
            return self.serializer(row).data
        else:
            return super(PurchasesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return ServicePurchase.objects \
            .prefetch_related("service") \
            .filter(account__user=self.request.user)


class OrdersDatatableView(PurchasesDatatableView):
    serializer = OrderSerializer

    def get_initial_queryset(self):
        return ServicePurchase.objects \
            .prefetch_related("service") \
            .filter(service__account__user=self.request.user)


class OrderDeliverablesDatatableView(BaseDatatableView):
    columns = [
        'title',
        'version',
        'annotate_files_count',
        'published',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: Deliverable

        if column == "created_at":
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
        elif column == "annotate_files_count":
            return intcomma(row.annotate_files_count)
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
            data = DeliverableSerializer(row).data
            data['files_count'] = row.annotate_files_count
            return data
        else:
            return super(OrderDeliverablesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Deliverable.objects.annotate(annotate_files_count=Count('deliverablefile')) \
            .filter(service_purchase=self.kwargs['pk'])


class PurchaseDeliverablesDatatableView(OrderDeliverablesDatatableView):
    def get_initial_queryset(self):
        return Deliverable.objects.annotate(annotate_files_count=Count('deliverablefile')) \
            .filter(service_purchase=self.kwargs['pk'], published=True)


class DeliverableFilesDatatableView(BaseDatatableView):
    columns = [
        'name',
        'size',
        'created_at',
        'data',
    ]

    def render_column(self, row, column):
        row: DeliverableFile

        if column == "created_at":
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
        elif column == "size":
            return row.size_display
        elif column == "data":
            data = DeliverableFileSerializer(row).data
            data['file_url'] = self.request.scheme + "://" + self.request.META['HTTP_HOST'] + row.file.url
            return data
        else:
            return super(DeliverableFilesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return DeliverableFile.objects.filter(deliverable=self.kwargs['pk'])


class DeliverableUploadView(View):
    def post(self, request, *args, **kwargs):
        f: UploadedFile = request.FILES['file']
        if f is not None:
            file_name = uuid.uuid4().urn[9:] + '.' + f.name.split('.')[-1]

            folder = "deliverables"
            create_folder_if_not_exits(folder)

            file_path = os.path.join(settings.BASE_DIR, "media", folder, file_name)

            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            deliverable_file = DeliverableFile()
            deliverable_file.deliverable_id = kwargs['pk']
            deliverable_file.name = f.name
            deliverable_file.file = folder + "/" + file_name
            deliverable_file.size = f.size
            deliverable_file.save()

        return JsonResponse({"response_code": 200}, safe=False)


class ChatMessageUploadView(View):
    def post(self, request, *args, **kwargs):
        f: UploadedFile = request.FILES['file']
        if f is not None:
            file_name = uuid.uuid4().urn[9:] + '.' + f.name.split('.')[-1]

            folder = "chat_files"
            create_folder_if_not_exits(folder)

            file_path = os.path.join(settings.BASE_DIR, "media", folder, file_name)

            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            chat_message = ChatMessage()
            chat_message.service_purchase_id = kwargs['pk']
            chat_message.account = request.user.account
            chat_message.is_file = True
            chat_message.file_name = f.name
            chat_message.file_size = f.size
            chat_message.file = folder + "/" + file_name
            chat_message.save()

            ChatMessageSubscription.broadcast(group=ChatMessageSubscription.name.format(kwargs['pk']),
                                              payload=chat_message.id.urn[9:])

        return JsonResponse({"response_code": 200}, safe=False)


class ServiceOptionsDatatableView(BaseDatatableView):
    currency = None
    columns = [
        'label',
        'delay',
        'price',
        'published',
        'created_at',
        'data'
    ]

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.currency = param_currency()

    def render_column(self, row, column):
        row: ServiceOption

        if column == "created_at":
            return date_filter(row.created_at) + " " + time_filter(row.created_at)
        elif column == "delay":
            return row.delay_display
        elif column == "price":
            return row.price_display + ' ' + self.currency
        elif column == "published":
            class_name = 'warning'
            if row.published:
                class_name = 'success'
            return '<span style="height: 5px" class="label label-lg font-weight-bold label-square label-inline label-light-{}">{}</span>' \
                .format(class_name, row.published_display)
        elif column == "data":
            return ServiceOptionsSerializer(row).data
        else:
            return super(ServiceOptionsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return ServiceOption.objects.filter(service=self.kwargs["pk"]).all()
