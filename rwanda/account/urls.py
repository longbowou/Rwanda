from django.urls import path

from rwanda.account.views import DepositsDatatableView

urlpatterns = [
    path('deposits.json', DepositsDatatableView.as_view()),
]
