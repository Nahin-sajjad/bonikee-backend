from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.hr.models.employee import Employee
from apps.hr.serializers.employee import EmployeeSerializer

from apps.share.views import get_tenant_user, number_generate


import json
from datetime import datetime


class EmployeeView(generics.ListCreateAPIView):
    """
    API view for retrieving a list of employees and creating new employee records.

    This view allows users to retrieve a list of employees for the current tenant
    and create new employee records.

    Attributes:
        queryset (QuerySet): The queryset to retrieve employee records for the current tenant.
        serializer_class (EmployeeSerializer): The serializer class for the Employee model.
    """

    queryset = Employee
    serializer_class = EmployeeSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get a queryset of employee records for the current tenant.

        Returns:
            QuerySet: A queryset of employee records.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            employee = tenant.employee_base_models.all().order_by("-created_at")
            return employee
        else:
            print("Tenant id not found")

    def create(self, request):
        """
        Create a new employee record.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response indicating success or failure.
        """
        data = json.loads(request.data["values"])
        tenant = get_tenant_user(self).tenant
        serializer = self.get_serializer(data=data)
        with transaction.atomic():
            try:
                try:
                    last_number = tenant.employee_base_models.last().employee_service_id
                except:
                    last_number = f"EMP-{datetime.now().year}-{0}"
                employee_service_id = number_generate(last_number)

                photo = request.data.get("photo", None)

                if serializer.is_valid():
                    serializer.save(
                        tenant=tenant,
                        photo=photo,
                        employee_service_id=employee_service_id,
                    )
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting an employee record.

    This view allows users to retrieve, update, and delete an existing employee record.

    Attributes:
        queryset (QuerySet): The queryset to retrieve employee records for the current tenant.
        serializer_class (EmployeeSerializer): The serializer class for the Employee model.
    """

    queryset = Employee
    serializer_class = EmployeeSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, *args, **kwargs):
        """
        Update an existing employee record.

        Args:
            request (Request): The HTTP request object.
            pk (int): The primary key of the employee record to be updated.

        Returns:
            Response: The HTTP response indicating success or failure.
        """
        data = json.loads(request.data["values"])
        pk = kwargs.get("pk")
        tenant = get_tenant_user(self).tenant
        employee_obj = tenant.employee_base_models.get(id=pk)
        serializer = self.get_serializer(employee_obj, data=data)
        with transaction.atomic():
            try:
                photo = request.data.get("photo", employee_obj.photo)
                if serializer.is_valid():
                    serializer.save(tenant=tenant, photo=photo)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    print(serializer.errors)
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
