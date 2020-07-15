# Register your models here.
from django.contrib import admin

from rwanda.core.models import *

admin.site.register(Parameters)
admin.site.register(User)
admin.site.register(Account)
admin.site.register(Admin)
admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(ServiceOption)
admin.site.register(ServiceMedia)
admin.site.register(Comment)
admin.site.register(SellerPurchase)
admin.site.register(SellerPurchaseServiceOption)
admin.site.register(Litigation)
admin.site.register(Chat)
