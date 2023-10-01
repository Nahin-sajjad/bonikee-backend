from django.db import models
from apps.share.models.base_model import BaseModel
from apps.procurement.models.receipt import Receipt, ReceiptLineItem

class BillPay(BaseModel):
    STATUS = (
        (1,'Partially Bill'),
        (2, 'Fully Bill'),
        (3,'Waiting For Bill')
    )
    bill_num = models.CharField(max_length=100)
    bill_dt = models.DateTimeField(auto_now=True)
    pay_method = models.CharField(max_length=100)
    adv_amt = models.FloatField(default=0)
    cash_amt = models.FloatField(default=0)
    bill_amt = models.FloatField(default=0)
    status = models.SmallIntegerField(default=3,blank=True,null=True, choices=STATUS)
    
    recpt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="bill_pays")
    
    class Meta:
        db_table = 'PROC_Bill_Pay'
        
        
class BillPayLineItem(BaseModel):
    bill = models.ForeignKey(BillPay, on_delete=models.CASCADE, related_name="pays_line_items")
    recpt_item = models.ForeignKey(ReceiptLineItem, on_delete=models.CASCADE, related_name="pays_line_items")
    
    class Meta:
        db_table = 'PROC_Bill_Pay_line_Item'
        