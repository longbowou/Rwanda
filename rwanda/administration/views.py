from django.template.defaultfilters import date as date_filter, time as time_filter
from django_datatables_view.base_datatable_view import BaseDatatableView

from rwanda.account.models import Refund, RefundWay
from rwanda.account.serializers import RefundSerializer, RefundWaySerializer, ParameterSerializer
from rwanda.account.views import ServicesDatatableView as AccountServicesDatatableView, \
    RefundsDatatableView as AccountRefundsDatatableView
from rwanda.administration.models import Parameter
from rwanda.administration.serializers import LitigationSerializer, ServiceCategorySerializer
from rwanda.purchase.models import Litigation
from rwanda.service.models import Service, ServiceCategory


class DisputesDatatableView(BaseDatatableView):
    columns = [
        'title',
        'status',
        'decision',
        'account',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: Litigation

        if column == "created_at":
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
        elif column == "status":
            class_name = 'dark'
            if row.handled:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.status_display)
        elif column == "decision":
            if row.handled:
                class_name = 'danger'
                if row.approved:
                    class_name = 'success'

                return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                    .format(class_name, row.decision_display)
        elif column == "account":
            return row.account.user.username
        elif column == "data":
            return LitigationSerializer(row).data
        else:
            return super(DisputesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Litigation.objects.prefetch_related("account", "account__user")


class ServicesDatatableView(AccountServicesDatatableView):
    columns = [
        'title',
        'category',
        'status',
        'account',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: Service

        if column == "account":
            return row.account.user.first_name
        else:
            return super(ServicesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Service.objects.prefetch_related('service_category', 'account__user').all()


class ServiceCategoriesDatatableView(BaseDatatableView):
    columns = [
        'label',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: ServiceCategory

        if column == "created_at":
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
        elif column == "data":
            return ServiceCategorySerializer(row).data
        else:
            return super(ServiceCategoriesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return ServiceCategory.objects.all()


class RefundsDatatableView(AccountRefundsDatatableView):
    columns = [
        'amount',
        'status',
        'refund_way',
        'phone_number',
        'created_at',
        'data',
    ]

    def render_column(self, row, column):
        row: Refund

        if column == "data":
            return RefundSerializer(row).data
        else:
            return super(RefundsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Refund.objects.prefetch_related("refund_way")


class RefundWaysDatatableView(BaseDatatableView):
    columns = [
        'name',
        'country_code',
        'published',
        'created_at',
        'data',
    ]

    def render_column(self, row, column):
        row: RefundWay

        if column == "published":
            class_name = 'warning'
            if row.published:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.published_display)
        elif column == "created_at":
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
        elif column == "data":
            return RefundWaySerializer(row).data
        else:
            return super(RefundWaysDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return RefundWay.objects.all()


class ParametersDatatableView(BaseDatatableView):
    columns = [
        'label',
        'value',
        'created_at',
        'data',
    ]

    def render_column(self, row, column):
        row: Parameter

        if column == "created_at":
            return date_filter(row.created_at) + ' ' + time_filter(row.created_at)
        elif column == "data":
            return ParameterSerializer(row).data
        else:
            return super(ParametersDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Parameter.objects.all()
