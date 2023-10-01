from django.db import models
from apps.share.models.base_model import BaseModel
from apps.procurement.models.receipt import Receipt,ReceiptLineItem

class PurReturn(BaseModel):
    return_num = models.CharField(max_length=100)
    return_dt = models.DateTimeField(auto_now=True)
    return_note = models.CharField(blank=True,null=True,max_length=1000)
    return_amt = models.FloatField(default=0)
    
    recpt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="pur_returns")
    
    class Meta:
        db_table = 'PROC_Pur_Return'
        

class PurReturnLineItem(BaseModel):
    return_qty = models.FloatField(default=0)
    
    pur_retrn = models.ForeignKey(PurReturn, on_delete=models.CASCADE, related_name='pur_return_line_items', blank=True, null=True)
    recpt_item = models.ForeignKey(ReceiptLineItem, on_delete=models.CASCADE, related_name="pur_return_line_items", blank=True, null=True)
    
    class Meta:
        db_table = 'PROC_Pur_Return_Line_Item'
        