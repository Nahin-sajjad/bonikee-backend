from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.hr.models.department import Department
from apps.hr.serializers.department import DepartmentSerializer

from apps.share.views import get_tenant_user


class DepartmentView(generics.ListCreateAPIView):
    """
    API view for retrieving a list of departments and creating new department records.

    This view allows users to retrieve a list of departments for the current tenant
    and create new department records.

    Attributes:
        queryset (QuerySet): The queryset to retrieve department records for the current tenant.
        serializer_class (DepartmentSerializer): The serializer class for the Department model.
    """

    queryset = Department
    serializer_class = DepartmentSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get a queryset of department records for the current tenant.

        Returns:
            QuerySet: A queryset of department records.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            department = tenant.department_base_models.all().order_by("-created_at")
            return department
        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        """
        Create a new department record.

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


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual department records.

    This view allows users to retrieve, update, and delete specific department records.

    Attributes:
        queryset (QuerySet): The queryset to retrieve department records for the current tenant.
        serializer_class (DepartmentSerializer): The serializer class for the Department model.
    """

    queryset = Department
    serializer_class = DepartmentSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )
