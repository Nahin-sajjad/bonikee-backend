from django.db import models

from apps.share.models.base_model import BaseModel


class Brand(BaseModel):
    # id
    brand_name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    brand_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = "INV_Brand"

    def __str__(self) -> str:
        return self.brand_name
