from django.urls import path

from rwanda.account.views import ServiceOptionsDatatableView
from rwanda.administration.views import DisputesDatatableView, ServiceCategoriesDatatableView, ServicesDatatableView

urlpatterns = [
    path('disputes.json', DisputesDatatableView.as_view()),
    path('service-categories.json', ServiceCategoriesDatatableView.as_view()),
    path('services.json', ServicesDatatableView.as_view()),
    path('service/<uuid:pk>/options.json', ServiceOptionsDatatableView.as_view()),
]
