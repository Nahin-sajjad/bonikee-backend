from django.db import models
from apps.share.models.base_model import BaseModel


# Create your models here.
class Vendor(BaseModel):
    vendor_name = models.CharField(
        max_length=250,
        db_index=True,
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    company = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = "VM_Vendor"
        unique_together = ("vendor_name", "tenant")
