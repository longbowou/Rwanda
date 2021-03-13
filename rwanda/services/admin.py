from django.contrib import admin

from rwanda.services.models import ServiceCategory, Service, ServiceOption, ServiceMedia, ServiceComment

admin.site.register(ServiceCategory)
admin.site.register(Service)
admin.site.register(ServiceOption)
admin.site.register(ServiceMedia)
admin.site.register(ServiceComment)
