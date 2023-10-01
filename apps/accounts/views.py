from django.contrib.auth.models import Permission
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CustomGroup

from apps.accounts.permissions import GroupPermission

from .serializers import PermissionSerializer, GroupSerializer

from apps.share.services.tenant_error_logger import TenantLogger


class PermissionView(generics.ListCreateAPIView):
    """
    View for listing and creating permission objects.

    This view excludes specific models' permissions from the list.

    Attributes:
        serializer_class (Serializer): The serializer class for Permission objects.
    """

    queryset = Permission
    serializer_class = PermissionSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset of Permission objects, excluding permissions related to specific models.

        Returns:
            QuerySet: Filtered queryset of Permission objects.
        """

        # Define a list of models you want to exclude from permissions
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
        queryset = Permission.objects.exclude(excluded_models_q)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        List permission objects and provide nested permissions.

        Returns:
            Response: JSON response containing permission data and nested permissions.
        """

        queryset = self.get_queryset()

        # Get the nested array response using the PermissionSerializer method
        nested_permissions = self.get_serializer().get_nested_permissions(queryset)

        return Response(nested_permissions)


class GroupView(generics.ListCreateAPIView):
    """
    View for listing and creating custom groups associated with a tenant.

    Attributes:
        serializer_class (Serializer): The serializer class for CustomGroup objects.
        queryset (QuerySet): The queryset used to fetch CustomGroup instances.
    """

    queryset = CustomGroup
    serializer_class = GroupSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset of CustomGroup objects associated with the current tenant.

        Returns:
            QuerySet: Filtered queryset of CustomGroup objects.
        """
        tenant = self.request.tenant
        groups = tenant.customgroup_base_models.all()
        return groups

    def create(self, request, *args, **kwargs):
        """
        Create a new custom group for the current tenant.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: JSON response indicating the success or failure of the creation.
        """
        tenant_logger = TenantLogger(request)

        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save(tenant=request.tenant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                tenant_logger.error(serializer.errors)
                return Response(
                    "Group name already exists", status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            tenant_logger.error(e)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a custom group associated with a tenant.

    Attributes:
        serializer_class (Serializer): The serializer class for CustomGroup objects.
        queryset (QuerySet): The queryset used to fetch CustomGroup instances.
    """

    queryset = CustomGroup
    serializer_class = GroupSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, *args, **kwargs):
        """
        Update a custom group associated with the current tenant.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: JSON response indicating the success or failure of the update.
        """
        tenant_logger = TenantLogger(request)
        pk = kwargs.get("pk")
        group_obj = request.tenant.customgroup_base_models.get(id=pk)

        try:
            serializer = self.get_serializer(group_obj, data=request.data)

            if serializer.is_valid():
                serializer.save(tenant=request.tenant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                tenant_logger.error(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            tenant_logger.error(e)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
