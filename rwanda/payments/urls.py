from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from rwanda.payments.views import PaymentView

urlpatterns = [
    path('confirmation', csrf_exempt(PaymentView.as_view()), name='payments-confirmation'),
]
