from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.clients.models import TenantUser
from apps.clients.serializers.tenant_users import TenantUserSerializer
from apps.share.views import get_tenant_user


class TenantUserListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating TenantUser instances.

    This view allows listing TenantUser instances belonging to the user's tenant
    and creating new ones.

    Attributes:
        queryset (QuerySet): The queryset used to fetch TenantUser instances.
        serializer_class (Serializer): The serializer class for TenantUser instances.
    """

    queryset = TenantUser
    serializer_class = TenantUserSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset of TenantUser instances based on the user's tenant.

        Returns:
            QuerySet: A filtered queryset of TenantUser instances.

        Raises:
            Exception: If the user's data does not exist.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant

            # Fetch all tenant users excluding superusers
            tenant_users = tenant.tenant_tenant_users.all()
            # tenant_users = tenant.tenant_tenant_users.all().exclude(user__is_superuser=True)
            return tenant_users
        else:
            raise Exception("Sorry! Your data does not exist.")
