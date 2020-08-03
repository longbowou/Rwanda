from django.contrib import admin

from rwanda.purchase.models import ServicePurchase, ServicePurchaseServiceOption, Litigation, Chat

admin.site.register(ServicePurchase)
admin.site.register(ServicePurchaseServiceOption)
admin.site.register(Litigation)
admin.site.register(Chat)
