from django.contrib import admin

from rwanda.account.models import Deposit, Refund

admin.register(Deposit)
admin.register(Refund)
