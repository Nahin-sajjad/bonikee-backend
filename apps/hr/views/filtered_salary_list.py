from django.db.models import Sum

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.hr.models.salary import Salary
from apps.hr.serializers.employee_salary import EmployeeSalarySerializer
from apps.hr.serializers.salary import SalarySerializer

from apps.share.views import validate_tenant_user

from datetime import datetime
import json


class FilterSalaryListView(APIView):
    """
    API view for filtering and listing employee salaries based on certain criteria.

    Attributes:
        queryset (QuerySet): The queryset for retrieving salaries.
        serializer_class (Serializer): The serializer class for employee salaries.
    """

    queryset = Salary
    serializer_class = EmployeeSalarySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get(self, request):
        """
        Handle GET requests to filter and list employee salaries.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response containing the filtered employee salary data.
        """
        tenant = self.request.tenant
        user = self.request.user

        valid = validate_tenant_user(tenant=tenant, user=user)
        if valid:
            data = json.loads(request.GET.get("form_data"))
            employees = tenant.employee_base_models.filter(
                emp_wage_type=data["emp_type"]
            ).order_by("-created_at")

            employee_salaries = []

            from_date = datetime.fromisoformat(data["from"][:-1])
            to_date = datetime.fromisoformat(data["to"][:-1])

            for employee in employees:
                employee_serializer = self.serializer_class(employee)
                salary_data = dict(employee_serializer.data)
                salary = Salary.objects.filter(
                    employee=employee, dt_from__gte=from_date, dt_to__lte=to_date
                )
                if salary.exists():
                    salary_data["deduction"] = salary.aggregate(Sum("deduct"))[
                        "deduct__sum"
                    ]
                    salary_data["bonus"] = salary.aggregate(Sum("bonus"))["bonus__sum"]
                    salary_data["advance"] = salary.aggregate(Sum("advance"))[
                        "advance__sum"
                    ]
                    salary_data["paid"] = (
                        salary.aggregate(Sum("salary"))["salary__sum"]
                        + salary_data["advance"]
                    )
                    salary_data["deduct"] = salary.aggregate(Sum("deduct"))[
                        "deduct__sum"
                    ]
                    salary_data["due"] = (
                        employee.salary
                        - salary_data["deduction"]
                        + salary_data["bonus"]
                        - salary_data["paid"]
                    )
                    salary_data["status"] = 2 if salary_data["due"] > 0 else 1
                    salary_data["status_list"] = (
                        ["error", "Unpaid"]
                        if salary_data["due"] > 0
                        else ["success", "Paid"]
                    )
                    salary_data["salary_data"] = SalarySerializer(
                        salary, many=True
                    ).data
                else:
                    salary_data["deduction"] = 0
                    salary_data["bonus"] = 0
                    salary_data["due"] = 0
                    salary_data["advance"] = 0
                    salary_data["paid"] = 0
                    salary_data["deduct"] = 0
                    salary_data["status"] = 2
                    salary_data["status_list"] = ["error", "Unpaid"]
                    salary_data["salary_data"] = []
                employee_salaries.append(salary_data)
            return Response(employee_salaries)
        else:
            return Response("Tenant not valid", status=status.HTTP_404_NOT_FOUND)
