from rest_framework import serializers

from apps.hr.models.salary import Salary


class SalarySerializer(serializers.ModelSerializer):
    dt_from = serializers.DateTimeField(format='%Y-%m-%d')
    dt_to = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = Salary
        fields = ['id', 'dt_from', 'dt_to', 'deduct', 'due',
                  'advance', 'salary', 'bonus', 'status', 'employee']
