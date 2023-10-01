from rest_framework import serializers
from apps.hr.models.attendance import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    # attend_status = serializers.ChoiceField(choices= Attendance.ATTEND_STATUS)
    attend_status_show = serializers.CharField(source='get_attend_status_display', read_only=True)    
    class Meta:
        model = Attendance
        fields = (
            'id', 
            'date',
            'week',
            'attend_status',
            'time',
            'comment',
            'employee',
            'attend_status_show'
            
        )
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['employee_name'] = instance.employee.name if instance.employee else None

        return representation