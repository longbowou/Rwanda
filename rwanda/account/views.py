from django.template.defaultfilters import date
from django_datatables_view.base_datatable_view import BaseDatatableView

from rwanda.account.models import Deposit


class DepositsDatatableView(BaseDatatableView):
    columns = [
        'amount',
        'created_at',
    ]

    def render_column(self, row, column):
        if column == "created_at":
            return date(row.created_at)
        else:
            return super(DepositsDatatableView, self).render_column(row, column)

    def get_initial_queryset(self):
        return Deposit.objects.filter(account__user=self.request.user).order_by("-created_at")
