from django.db import models

from apps.share.models.base_model import BaseModel


class Warehouse(BaseModel):
    # id
    warehouse_name = models.CharField(max_length=250)
    warehouse_sn = models.CharField(max_length=250)
    location = models.CharField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.warehouse_name

    class Meta:
        db_table = "INV_Warehouse"
        ordering = ("-is_primary", "-id")
