from django.db import models
from apps.share.models.base_model import BaseModel
from apps.customers.models.customer import Customer

class CustomerCollection(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_collections",)
    collection_num = models.CharField(max_length=20, blank=True, null=True)
    amount = models.FloatField(default=0)
    note = models.CharField(max_length=264, blank=True, null=True)

    STATE = (
        (1, 'Open'),
        (2, 'Collected'),
        (2, 'Canceled')
    )
    status = models.IntegerField(choices=STATE, default=1)

    class Meta:
        db_table = "FM_Collection"