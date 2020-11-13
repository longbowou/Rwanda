from django.urls import path

from rwanda.administration.views import DisputesDatatableView, ServiceCategoriesDatatableView, ServicesDatatableView

urlpatterns = [
    path('disputes.json', DisputesDatatableView.as_view()),
    path('service-categories.json', ServiceCategoriesDatatableView.as_view()),
    path('services.json', ServicesDatatableView.as_view()),
]
