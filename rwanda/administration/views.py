from django.template.defaultfilters import date as date_filter, time as time_filter
from django_datatables_view.base_datatable_view import BaseDatatableView

from rwanda.administration.serializers import LitigationSerializer
from rwanda.purchase.models import Litigation


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
