from django.db.models import Q, Sum

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.hr.models.salary import Salary
from apps.hr.serializers.salary import SalarySerializer
from apps.hr.models.employee import Employee

from apps.share.views import get_tenant_user
from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime, date


class SalaryView(generics.ListCreateAPIView):
    """
    API view for listing and creating employee salaries.

    Attributes:
        queryset (QuerySet): The queryset for retrieving salaries.
        serializer_class (Serializer): The serializer class for employee salaries.
    """

    queryset = Salary
    serializer_class = SalarySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset of employee salaries for the current tenant.

        Returns:
            QuerySet: The queryset of employee salaries.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            salary_list = tenant.employee_base_models.all().order_by("-created_at")
            return salary_list
        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        """
        Create a new employee salary and associated transactions.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response.
        """
        user_tenant = get_tenant_user(self)
        data = request.data
        date_from = datetime.fromisoformat(data["dt_from"][:-1])
        date_to = datetime.fromisoformat(data["dt_to"][:-1])
        salary = Salary.objects.filter(
            Q(employee_id=data["employee"])
            & Q(dt_from__gte=date_from)
            & Q(dt_to__lte=date_to)
        )
        if salary.exists():
            return Response("Salary already exists", status=status.HTTP_302_FOUND)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                salary = serializer.save(tenant=tenant)

                # Start employee advance collection
                employee = Employee.objects.get(id=data["employee"])
                employee.advance_due = employee.advance_due - float(data["advance"])
                employee.save()
                # End employee advance collection

                # Start transaction manager collection
                salary_today = Salary.objects.filter(
                    created_at__year=date.today().year,
                    created_at__month=date.today().month,
                    created_at__day=date.today().day,
                )
                paid_salary_today = salary_today.aggregate(Sum("salary"))["salary__sum"]
                advance_salary_today = salary_today.aggregate(Sum("advance"))[
                    "advance__sum"
                ]
                transaction_manager = TransactionManager(
                    tenant=tenant, tran_number=salary.created_at
                )
                transaction_manager.transaction_create_or_update(
                    tran_group=103,
                    amount=paid_salary_today + advance_salary_today,
                    tran_type=1011,
                    tran_head=6,
                )
                # End transaction manager collection

                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting an employee salary.

    Attributes:
        queryset (QuerySet): The queryset for retrieving salaries.
        serializer_class (Serializer): The serializer class for employee salaries.
    """

    queryset = Salary
    serializer_class = SalarySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests to delete an employee salary.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response.
        """
        salary = self.get_object()

        # Start employee advance collection
        employee = Employee.objects.get(id=salary.employee_id)
        employee.advance_due = employee.advance_due + salary.advance
        employee.save()
        # End employee advance collection

        return super().delete(request, *args, **kwargs)
