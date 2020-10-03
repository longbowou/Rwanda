from django.contrib import admin

from rwanda.purchase.models import ServicePurchase, ServicePurchaseServiceOption, Litigation, ChatMessage

admin.site.register(ServicePurchase)
admin.site.register(ServicePurchaseServiceOption)
admin.site.register(Litigation)
admin.site.register(ChatMessage)
