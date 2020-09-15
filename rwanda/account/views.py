from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import date
from django.template.defaultfilters import date as date_filter
from django_datatables_view.base_datatable_view import BaseDatatableView
from rest_framework import serializers

from rwanda.account.models import Deposit, Refund
from rwanda.service.models import Service


class DepositsDatatableView(BaseDatatableView):
    columns = [
        'amount',
        'created_at',
    ]

    def render_column(self, row, column):
        if column == "amount":
            return intcomma(row.amount)
        elif column == "created_at":
            return date(row.created_at)
        else:
            return super(DepositsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Deposit.objects.filter(account__user=self.request.user).order_by("-created_at")


class RefundsDatatableView(BaseDatatableView):
    columns = [
        'amount',
        'phone_number',
        'created_at',
    ]

    def render_column(self, row, column):
        if column == "amount":
            return intcomma(row.amount)
        elif column == "created_at":
            return date(row.created_at)
        else:
            return super(RefundsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Refund.objects.filter(account__user=self.request.user).order_by("-created_at")


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
        if column == "created_at":
            return date_filter(row.created_at)
        elif column == "delay":
            return intcomma(row.delay)
        elif column == "activated":
            class_name = 'warning'
            if row.activated:
                class_name = 'success'

            return '<span style="height: 10px" class="label label-lg font-weight-bold label-inline label-light-{}">{}</span>' \
                .format(class_name, row.activated_display)
        elif column == "published":
            class_name = 'warning'
            if row.published:
                class_name = 'success'

            return '<span style="height: 10px" class="label label-lg font-weight-bold label-inline label-light-{}">{}</span>' \
                .format(class_name, row.published_display)
        elif column == "data":
            return ServiceSerializer(row).data
        else:
            return super(ServicesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Service.objects.filter(account__user=self.request.user).order_by("-created_at").all()
