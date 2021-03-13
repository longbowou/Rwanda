from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Q
from django.template.defaultfilters import date as date_filter, time as time_filter
from django_datatables_view.base_datatable_view import BaseDatatableView

from rwanda.account.models import Refund, RefundWay
from rwanda.account.serializers import RefundSerializer, RefundWaySerializer, ParameterSerializer, UserSerializer
from rwanda.account.views import ServicesDatatableView as AccountServicesDatatableView, \
    RefundsDatatableView as AccountRefundsDatatableView
from rwanda.accounting.models import Operation
from rwanda.administration.models import Parameter
from rwanda.administration.serializers import LitigationSerializer, ServiceCategorySerializer
from rwanda.administration.utils import param_currency
from rwanda.purchases.models import Litigation
from rwanda.services.models import Service, ServiceCategory
from rwanda.users.models import User


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
            return date_filter(row.created_at) + '<br>' + time_filter(row.created_at)
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
            return str(row.account)
        elif column == "data":
            return LitigationSerializer(row).data
        else:
            return super(DisputesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Litigation.objects.prefetch_related("account", "account__user")


class ServicesDatatableView(AccountServicesDatatableView):
    columns = [
        'title',
        'service_category__label',
        'status',
        'published_by_admin',
        'account',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: Service

        if column == "account":
            return str(row.account)
        elif column == "published_by_admin":
            class_name = 'warning'
            if row.published_by_admin:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.published_by_admin_display)
        else:
            return super(ServicesDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Service.objects.prefetch_related('service_category', 'account__user').all()


class AccountServicesDatatableView(ServicesDatatableView):
    def get_initial_queryset(self):
        return Service.objects.prefetch_related('service_category', 'account__user').filter(
            account__user_id=self.kwargs['pk'])


class ServiceCategoriesDatatableView(BaseDatatableView):
    columns = [
        'label',
        'published',
        'index',
        'created_at',
        'data'
    ]

    def render_column(self, row, column):
        row: ServiceCategory

        if column == "created_at":
            return date_filter(row.created_at) + '<br>' + time_filter(row.created_at)
        elif column == "published":
            class_name = 'warning'
            if row.published:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.published_display)
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
        'payment__status',
        'refund_way',
        'phone_number',
        'account',
        'created_at',
        'data',
    ]

    def render_column(self, row, column):
        row: Refund

        if column == "account":
            return str(row.account)
        elif column == "payment__status":
            if row.payment is not None:
                class_name = 'dark'
                if row.payment.confirmed:
                    class_name = 'success'

                if row.payment.canceled:
                    class_name = 'danger'

                return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                    .format(class_name, row.payment.status_display)
        elif column == "data":
            return RefundSerializer(row).data
        else:
            return super(RefundsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Refund.objects.prefetch_related("refund_way", "account")


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
            return date_filter(row.created_at) + '<br>' + time_filter(row.created_at)
        elif column == "data":
            return ParameterSerializer(row).data
        else:
            return super(ParametersDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Parameter.objects.all()


class AccountDatatableView(BaseDatatableView):
    columns = [
        'first_name',
        'last_name',
        'username',
        'email',
        'phone_number',
        'is_active',
        'created_at',
        'data',
    ]

    def render_column(self, row, column):
        row: User

        if column == "is_active":
            class_name = 'warning'
            if row.is_active:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.is_active_display)
        elif column == "created_at":
            return date_filter(row.created_at) + '<br>' + time_filter(row.created_at)
        elif column == "data":
            return UserSerializer(row).data
        else:
            return super(AccountDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return User.objects.filter(~Q(account__isnull=True))


class AccountOperationsDatatableView(BaseDatatableView):
    currency = None
    columns = [
        'type',
        'amount',
        'description',
        'created_at',
    ]

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.currency = param_currency()

    def render_column(self, row, column):
        row: Operation

        if column == "type":
            class_name = 'primary'
            if row.credit:
                class_name = 'success'

            return '<span style="height: 5px" class="label label-lg font-weight-bold label-inline label-square label-light-{}">{}</span>' \
                .format(class_name, row.type_display)
        elif column == "amount":
            return intcomma(row.amount) + " " + self.currency
        elif column == "created_at":
            return date_filter(row.created_at) + '<br>' + time_filter(row.created_at)
        else:
            return super(AccountOperationsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Operation.objects.filter(account__user_id=self.kwargs['pk'])
