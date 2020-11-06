from django.urls import path

from rwanda.payments.views import PaymentView

urlpatterns = [
    path('confirmation', PaymentView.as_view(), name='payments-confirmation'),
]
