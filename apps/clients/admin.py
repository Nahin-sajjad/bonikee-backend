from django.contrib import admin

from apps.clients.models import ClientModel, TenantUser, DomainModel


admin.site.register(ClientModel)
admin.site.register(DomainModel)
admin.site.register(TenantUser)
