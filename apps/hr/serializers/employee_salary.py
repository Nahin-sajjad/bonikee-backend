from rest_framework import serializers
from apps.hr.models.employee import Employee

from apps.hr.models.attendance import Attendance


class EmployeeSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "name", "salary", "photo", "advance_due")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["wage_type"] = (
            "Part-Time" if instance.emp_wage_type == 1 else "Full-Time"
        )
        representation["emp_status"] = (
            "Active" if instance.status == 1 else "Terminated"
        )
        attendances = Attendance.objects.filter(employee=instance)

        representation["total_absences"] = attendances.filter(attend_status=2).count()

        representation["total_leaves"] = attendances.filter(attend_status=3).count()
        return representation
