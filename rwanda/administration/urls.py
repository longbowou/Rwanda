from django.urls import path

from rwanda.account.views import ServiceOptionsDatatableView
from rwanda.administration.views import DisputesDatatableView, ServiceCategoriesDatatableView, ServicesDatatableView, \
    RefundsDatatableView, RefundWaysDatatableView, ParametersDatatableView, AccountDatatableView, \
    AccountServicesDatatableView, AccountOperationsDatatableView

urlpatterns = [
    path('refunds.json', RefundsDatatableView.as_view()),
    path('refund-ways.json', RefundWaysDatatableView.as_view()),
    path('disputes.json', DisputesDatatableView.as_view()),
    path('parameters.json', ParametersDatatableView.as_view()),
    path('accounts.json', AccountDatatableView.as_view()),
    path('service-categories.json', ServiceCategoriesDatatableView.as_view()),
    path('services.json', ServicesDatatableView.as_view()),
    path('services/<uuid:pk>/options.json', ServiceOptionsDatatableView.as_view()),
    path('account/<uuid:pk>/services.json', AccountServicesDatatableView.as_view()),
    path('account/<uuid:pk>/operations.json', AccountOperationsDatatableView.as_view()),
]
