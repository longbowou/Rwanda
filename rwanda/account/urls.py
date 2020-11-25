from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from rwanda.account.views import PurchasesDatatableView, OrdersDatatableView, PurchaseDeliverablesDatatableView, \
    DeliverableUploadView, DepositsDatatableView, RefundsDatatableView, ServicesDatatableView, \
    ServiceOptionsDatatableView, ChatMessageUploadView, ServiceUploadView, \
    DeliverableFilesDatatableView, OrderDeliverablesDatatableView, ServicePreSaveUploadView, AvatarUploadView

urlpatterns = [
    path('deposits.json', DepositsDatatableView.as_view()),
    path('refunds.json', RefundsDatatableView.as_view()),
    path('services.json', ServicesDatatableView.as_view()),
    path('services/<uuid:pk>/options.json', ServiceOptionsDatatableView.as_view()),
    path('services/<uuid:pk>/upload', csrf_exempt(ServiceUploadView.as_view())),
    path('services/pre-save/upload', csrf_exempt(ServicePreSaveUploadView.as_view())),
    path('avatar/upload', csrf_exempt(AvatarUploadView.as_view())),

    path('orders.json', OrdersDatatableView.as_view()),
    path('orders/<uuid:pk>/deliverables.json', OrderDeliverablesDatatableView.as_view()),

    path('purchases.json', PurchasesDatatableView.as_view()),
    path('purchases/<uuid:pk>/deliverables.json', PurchaseDeliverablesDatatableView.as_view()),

    path('deliverables/<uuid:pk>/files.json', DeliverableFilesDatatableView.as_view()),
    path('deliverables/<uuid:pk>/upload', csrf_exempt(DeliverableUploadView.as_view())),

    path('chat-messages/<uuid:pk>/upload', csrf_exempt(ChatMessageUploadView.as_view())),
]
