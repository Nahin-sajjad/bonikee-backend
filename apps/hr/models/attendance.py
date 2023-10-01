from django.db import models
from apps.share.models.base_model import BaseModel
from .employee import Employee

class Attendance(BaseModel):
    date = models.DateTimeField(blank=True, null=True)
    week = models.IntegerField(default=0)
    
    ATTEND_STATUS = (
        (1, "Present"),
        (2, "Absent"),
        (3, "Late")
    )
    attend_status = models.IntegerField(choices=ATTEND_STATUS, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    time = models.CharField(max_length=164)
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING,  related_name="employee_attendance")
    
    
    class Meta:
        db_table = "HR_Attend"