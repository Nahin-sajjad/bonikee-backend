from django.db import models

from apps.share.models.base_model import BaseModel


class UOM(BaseModel):
    # id
    uom_name = models.CharField(max_length=250)
    TYPE_CHOICES = [
        ("1", "Length"),
        ("2", "Weight"),
        ("3", "Volume"),
    ]
    uom_type_cd = models.CharField(max_length=250, blank=True, null=True,  choices=TYPE_CHOICES)
    is_pack_unit = models.BooleanField(default=False)

    class Meta:
        db_table = "INV_UOM"
