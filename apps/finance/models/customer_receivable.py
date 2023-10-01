from django.db import models
from apps.share.models.base_model import BaseModel
from apps.customers.models.customer import Customer

class CustomerReceivable(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_receivables')
    receivable_num = models.CharField(max_length=20,) 
    amount = models.FloatField(default=0)
    note = models.CharField(max_length=264, blank=True, null=True)
    comitted_payment_date = models.DateTimeField(blank=True, null=True)

    STATE = (
        (1, 'Open'),
        (2, 'Received'),
        (2, 'Canceled')
    )
    status = models.IntegerField(choices=STATE, default=1)

    class Meta:
        db_table = "FM_Receivable"