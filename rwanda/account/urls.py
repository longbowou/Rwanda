from django.urls import path

from rwanda.account.views import DepositsDatatableView, RefundsDatatableView

urlpatterns = [
    path('deposits.json', DepositsDatatableView.as_view()),
    path('refunds.json', RefundsDatatableView.as_view()),
]
