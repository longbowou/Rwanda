from django.contrib import admin

from rwanda.users.models import User, Account, Admin

admin.site.register(User)
admin.site.register(Account)
admin.site.register(Admin)
