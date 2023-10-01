from django.contrib import admin
from .models import User, UserLogInfo

admin.site.register(User)
admin.site.register(UserLogInfo)


# # Register your models here.
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ('email', 'get_full_name', 'is_active', 'is_superuser', 'date_joined')
#     list_filter = ( 'is_active', 'is_superuser')
#     search_fields = ('email',)
#     date_hierarchy = 'date_joined'

#     def get_full_name(self, obj):
#         return obj.get_full_name()
#     get_full_name.short_description = 'Name'


# admin.site.register(User, CustomUserAdmin)

# admin.site.site_header = "GLASCUTR IMS"
# admin.site.site_title = "GLASCUTR IMS"
# admin.site.index_title = "Welcome to GLASCUTR IMS"
