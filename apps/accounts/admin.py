from django.contrib import admin
from django.contrib.auth.models import Group

from apps.accounts.models import CustomGroup

admin.site.unregister(Group)
admin.site.register(CustomGroup)
