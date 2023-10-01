from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.finance.models.inc_exp_type import IncExpType
from apps.finance.serializers.inc_exp_type import IncExpTypeSerializer

from apps.share.views import get_tenant_user


class IncExpTypeView(generics.ListCreateAPIView):
    """
    API view for listing and creating income and expense types.

    Permissions:
    - Users with specific group permissions or superusers can access this view.

    Methods:
    - GET: Retrieve a list of income and expense types.
    - POST: Create a new income and expense type.
    """

    queryset = IncExpType
    serializer_class = IncExpTypeSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset for listing income and expense types based on the user's tenant.

        Returns:
        - Queryset of income and expense types filtered by tenant.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            inc_exp_types = tenant.incexptype_base_models.all().order_by("-created_at")
            return inc_exp_types
        else:
            # Tenant not found, return an empty queryset
            return IncExpType.objects.none()

    def perform_create(self, serializer):
        """
        Perform the creation of a new income and expense type.

        Parameters:
        - serializer: The serializer instance.

        Returns:
        - Response with status code 201 for successful creation.
        - Response with status code 500 for server error.
        """
        user_tenant = get_tenant_user(self)

        if user_tenant is not None:
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": "An error occurred while creating the type."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"error": "Tenant id not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
