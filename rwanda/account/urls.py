from django.urls import path

from rwanda.account.views import DepositsDatatableView, RefundsDatatableView, ServicesDatatableView, \
    ServicePurchasesDatatableView

urlpatterns = [
    path('deposits.json', DepositsDatatableView.as_view()),
    path('refunds.json', RefundsDatatableView.as_view()),
    path('services.json', ServicesDatatableView.as_view()),
    path('service-purchases.json', ServicePurchasesDatatableView.as_view()),
]
