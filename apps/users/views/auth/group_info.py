from django.contrib.auth.models import Permission
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from apps.accounts.models import CustomGroup
from apps.accounts.serializers import PermissionSerializer

from apps.clients.models import TenantUser


class UserGroupInfoView(APIView):
    """
    API endpoint for retrieving a user's group permissions.

    Allows superusers to get all available permissions.
    Allows users to get permissions based on their assigned groups.

    Methods:
    - GET: Retrieve the user's group permissions.
    """

    # queryset = CustomGroup
    # permission_classes = (GroupPermission,)

    def get_permission_list(self):
        """
        Get a list of permissions excluding those related to certain models.

        Returns:
        - Queryset: List of permissions.
        """
        # Define a list of models you want to exclude
        excluded_models = [
            "clientmodel",
            "domainmodel",
            "contenttype",
            "outstandingtoken",
            "blacklistedtoken",
            "logentry",
        ]

        # Create a Q object to represent the OR condition for excluded models
        excluded_models_q = Q()
        for model_name in excluded_models:
            excluded_models_q |= Q(content_type__model=model_name)

        # Exclude permissions related to excluded models
        permissions = Permission.objects.exclude(excluded_models_q)
        return permissions

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve user's group permissions.

        Args:
        - request: The HTTP request object.

        Returns:
        - Response: JSON response containing permissions or an error message with appropriate status code.
        """
        try:
            user = self.request.user
            tenant_user = TenantUser.objects.get(user=user)

            if tenant_user.is_superuser:
                permission_list = self.get_permission_list()
                permission_list_data = PermissionSerializer().get_nested_permissions(
                    permission_list
                )
                return Response(permission_list_data)
            else:
                groups = CustomGroup.get_groups_for_user(user)
                if groups.exists():
                    permission_set = set()  # Create a set to store distinct permissions

                    for group in groups:
                        permissions_queryset = group.permissions.all()
                        permission_set.update(
                            permissions_queryset
                        )  # Update the set with permissions from the queryset

                    # Now, you have a set of distinct permissions from all the groups
                    permission_list_data = (
                        PermissionSerializer().get_nested_permissions(
                            list(permission_set)
                        )
                    )
                    return Response(permission_list_data)
                else:
                    return Response(
                        {"detail": "No custom group found for the user."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
        except TenantUser.DoesNotExist:
            return Response(
                {"detail": "Tenant user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
