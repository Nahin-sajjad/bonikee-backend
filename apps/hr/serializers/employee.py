from rest_framework import serializers
from apps.hr.models.employee import Employee
from datetime import datetime


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Employee model.

    This serializer is used to convert Employee model instances to JSON representations and vice versa.

    Attributes:
        status_label (CharField): A read-only field to display the human-readable status label.
        emp_wage_type_label (CharField): A read-only field to display the human-readable wage type label.
        doj (DateTimeField): A field to format the date of joining (doj) as 'yyyy-MM-dd'.
    """

    status_label = serializers.CharField(
        source="get_status_display", read_only=True, required=False
    )
    emp_wage_type_label = serializers.CharField(
        source="get_emp_wage_type_display", read_only=True, required=False
    )
    doj = serializers.DateTimeField(
        format="%Y-%m-%d"
    )  # Format the doj field as 'yyyy-MM-dd'

    class Meta:
        model = Employee
        fields = (
            "id",
            "name",
            "dept",
            "desig",
            "doj",
            "emp_wage_type",
            "hr_per_day",
            "salary",
            "status",
            "photo",
            "addr",
            "nid",
            "phone",
            "advance_due",
            "created_at",
            "edited_at",
            "status_label",
            "emp_wage_type_label",
            "employee_service_id",
        )

    def to_representation(self, instance):
        """
        Convert Employee model instance to JSON representation.

        Args:
            instance (Employee): The Employee model instance.

        Returns:
            dict: JSON representation of the Employee instance with additional computed fields.
        """
        representation = super().to_representation(instance)
        representation["dept_name"] = instance.dept.name if instance.dept else None
        representation["desig_name"] = instance.desig.name if instance.desig else None
        representation["doj"] = (
            instance.doj.strftime("%b %d, %Y") if instance.doj else None
        )
        representation["employee_service_id_label"] = (
            ["primary", instance.employee_service_id]
            if instance.employee_service_id
            else None
        )

        # Calculate the total advance for the current month
        current_month_str = datetime.now().month
        total_advance = 0
        advance_list = instance.employee_advance.filter(date__month=current_month_str)
        for i in advance_list:
            total_advance += i.advance
        representation["total_advance"] = total_advance

        return representation
