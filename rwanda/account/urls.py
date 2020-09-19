from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from rwanda.account.views import DepositsDatatableView, RefundsDatatableView, ServicesDatatableView, \
    PurchasesDatatableView, OrdersDatatableView, DeliverablesDatatableView, DeliverableUploadView, \
    DeliverableFilesDatatableView

urlpatterns = [
    path('deposits.json', DepositsDatatableView.as_view()),
    path('refunds.json', RefundsDatatableView.as_view()),
    path('services.json', ServicesDatatableView.as_view()),
    path('service-purchases.json', PurchasesDatatableView.as_view()),
    path('service-orders.json', OrdersDatatableView.as_view()),
    path('orders/<uuid:pk>/deliverables.json', DeliverablesDatatableView.as_view()),
    path('deliverables/<uuid:pk>/files.json', DeliverableFilesDatatableView.as_view()),
    path('deliverables/<uuid:pk>/upload', csrf_exempt(DeliverableUploadView.as_view())),
]
