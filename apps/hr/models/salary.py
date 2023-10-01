from django.db import models
from apps.share.models.base_model import BaseModel
from .employee import Employee


class Salary(BaseModel):
    dt_from = models.DateTimeField(blank=True, null=True)
    dt_to = models.DateTimeField(blank=True, null=True)
    deduct = models.FloatField(default=0)
    advance = models.FloatField(default=0)
    salary = models.FloatField(default=0)
    
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name="employee_salary",blank=True, null=True)

    bonus = models.FloatField(default=0)
    due = models.FloatField(default=0)
    STATUS = (
        (1, 'Paid'),
        (2, 'Unpaid'),
    )
    status = models.IntegerField(default=2, choices=STATUS)

    class Meta:
        db_table = "HR_Salary"
