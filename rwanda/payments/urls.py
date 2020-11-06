from django.urls import path

from rwanda.payments.views import PaymentView

urlpatterns = [
    path('confirmation/<uuid:pk>', PaymentView.as_view(), name='payments-confirmation'),
]
