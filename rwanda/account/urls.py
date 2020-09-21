from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from rwanda.account.views import DepositsDatatableView, RefundsDatatableView, ServicesDatatableView, \
    ServiceOptionsDatatableView
from rwanda.account.views import PurchasesDatatableView, OrdersDatatableView, PurchaseDeliverablesDatatableView, \
    DeliverableUploadView, \
    DeliverableFilesDatatableView, OrderDeliverablesDatatableView

urlpatterns = [
    path('deposits.json', DepositsDatatableView.as_view()),
    path('refunds.json', RefundsDatatableView.as_view()),
    path('services.json', ServicesDatatableView.as_view()),
    path('service/<uuid:pk>/options.json', ServiceOptionsDatatableView.as_view()),

    path('orders.json', OrdersDatatableView.as_view()),
    path('orders/<uuid:pk>/deliverables.json', OrderDeliverablesDatatableView.as_view()),

    path('purchases.json', PurchasesDatatableView.as_view()),
    path('purchases/<uuid:pk>/deliverables.json', PurchaseDeliverablesDatatableView.as_view()),

    path('deliverables/<uuid:pk>/files.json', DeliverableFilesDatatableView.as_view()),
    path('deliverables/<uuid:pk>/upload', csrf_exempt(DeliverableUploadView.as_view())),
]
