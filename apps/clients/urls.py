from django.urls import path
from apps.clients.views.tenant_users import TenantUserListView

urlpatterns = [
    # Define a URL pattern for the 'TenantUserListView' view.
    # When the URL 'users/' is accessed, it will invoke the 'TenantUserListView' view.
    # The name 'tenant_users' can be used to reverse this URL in templates or code.
    path("users/", TenantUserListView.as_view(), name="tenant_users"),
]
