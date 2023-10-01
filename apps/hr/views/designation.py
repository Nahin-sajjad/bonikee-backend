from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.hr.models.designation import Designation
from apps.hr.serializers.designation import DesignationSerializer

from apps.share.views import get_tenant_user


class DesignationView(generics.ListCreateAPIView):
    """
    API view for retrieving a list of designations and creating new designation records.

    This view allows users to retrieve a list of designations for the current tenant
    and create new designation records.

    Attributes:
        queryset (QuerySet): The queryset to retrieve designation records for the current tenant.
        serializer_class (DesignationSerializer): The serializer class for the Designation model.
    """

    queryset = Designation
    serializer_class = DesignationSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get a queryset of designation records for the current tenant.

        Returns:
            QuerySet: A queryset of designation records.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            designation = tenant.designation_base_models.all().order_by("-created_at")
            return designation
        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        """
        Create a new designation record.

        Args:
            request (Request): The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Keyword arguments.

        Returns:
            Response: The HTTP response indicating success or failure.
        """
        tenant = get_tenant_user(self).tenant
        serializer = self.get_serializer(data=request.data)
        with transaction.atomic():
            try:
                if serializer.is_valid():
                    serializer.save(tenant=tenant)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DesignationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual designation records.

    This view allows users to retrieve, update, and delete specific designation records.

    Attributes:
        queryset (QuerySet): The queryset to retrieve designation records for the current tenant.
        serializer_class (DesignationSerializer): The serializer class for the Designation model.
    """

    queryset = Designation
    serializer_class = DesignationSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )
