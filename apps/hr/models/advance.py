from django.db import models
from apps.share.models.base_model import BaseModel
from .employee import Employee

class Advance(BaseModel):
    date =  models.DateTimeField(blank=True, null=True)
    advance =  models.FloatField(default=0)
    
    ADV_TYPE = (
        (1, 'Loan'),
        (2, 'Advance')
    )
    adv_type = models.IntegerField(choices=ADV_TYPE, blank=True, null=True)
    
    employee =  models.ForeignKey(Employee, on_delete=models.DO_NOTHING, related_name='employee_advance', blank=True, null=True)
    
    
    class Meta:
        db_table = 'HR_Advance'