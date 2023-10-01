from django.db import models
from apps.share.models.base_model import BaseModel
from apps.hr.models.department import Department
from apps.hr.models.designation import Designation


class Employee(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True)
    employee_service_id = models.CharField(max_length=100, blank=True, null=True)
    doj = models.DateTimeField(blank=True, null=True)

    WAGE_TYPE = (
        (1, "Part-Time"),
        (2, "Full-Time"),
    )
    emp_wage_type = models.IntegerField(choices=WAGE_TYPE, blank=True, null=True)
    hr_per_day = models.CharField(max_length=50, blank=True, null=True)
    salary = models.FloatField(default=0)

    STATUS = ((1, "Active"), (2, "Terminated"))
    status = models.IntegerField(choices=STATUS, blank=True, null=True)
    photo = models.ImageField(blank=True, null=True)
    addr = models.CharField(max_length=500, blank=True, null=True)
    nid = models.BigIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    advance_due = models.FloatField(default=0)

    dept = models.ForeignKey(
        Department,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_department",
    )
    desig = models.ForeignKey(
        Designation,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_designation",
    )

    class Meta:
        db_table = "HR_Employee"

    def __str__(self) -> str:
        return self.name
