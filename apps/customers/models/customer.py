from django.db import models
from apps.share.models.base_model import BaseModel

class Customer(BaseModel):
    customer_name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'CM_Customer'