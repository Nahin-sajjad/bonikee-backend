from rest_framework import permissions

from apps.accounts.models import CustomGroup

from apps.clients.models import TenantUser


class GroupPermission(permissions.BasePermission):
    """
    Custom permission to check if the user has specific permissions within a group.
    """

    def get_method(self, method, model_name):
        # Helper function to determine the codename based on HTTP method and model name
        if method == "GET":
            codename = f"view_{model_name}"
        elif method == "POST":
            codename = f"add_{model_name}"
        elif method == "PUT" or method == "PATCH":
            codename = f"change_{model_name}"
        elif method == "DELETE":
            codename = f"delete_{model_name}"
        return codename

    def has_permission(self, request, view):
        user = request.user
        tenant_user = TenantUser.objects.get(user=user)

        if tenant_user.is_superuser:
            # Superusers have permission to perform any action
            return True
        else:
            method = request.method
            model_name = view.queryset.__name__.lower()
            codename = self.get_method(method=method, model_name=model_name)

            if codename.startswith("view_"):
                # Users have permission to view data
                return True

            groups = CustomGroup.objects.filter(users=user)
            is_exists = False

            for group in groups:
                # Check if the user belongs to any group that has the required permission
                permission_check = group.permissions.filter(codename=codename)

                if permission_check.exists():
                    is_exists = True
                    break

            return is_exists
