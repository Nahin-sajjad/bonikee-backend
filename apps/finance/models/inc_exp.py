from django.db import models

from apps.share.models.base_model import BaseModel


class IncExp(BaseModel):
    num = models.CharField(max_length=100, blank=True, null=True)
    type = models.PositiveIntegerField()
    source_type = models.PositiveIntegerField()
    dt = models.DateTimeField()
    amt = models.FloatField(default=0)
    ref_num = models.CharField(max_length=100, blank=True, null=True)
    pay_method = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "FM_INC_EXP"
