from django.urls import path

from rwanda.administration.views import DisputesDatatableView

urlpatterns = [
    path('disputes.json', DisputesDatatableView.as_view()),
]
