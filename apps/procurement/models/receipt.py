from django.db import models
from apps.share.models.base_model import BaseModel
from apps.vendors.models.vendor import Vendor
from apps.inventories.models.warehouse import Warehouse
from apps.users.models import User
from apps.inventories.models.item import Item
from apps.inventories.models.uom import UOM
from apps.share.views import generate_stock_identity

class Receipt(BaseModel):
    STATUS = (
        (1,'Created'),
        (2, 'Closed')
    )
    recpt_num = models.CharField(max_length=100, blank=True, null=True)
    recpt_dt = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(default=1,blank=True,null=True, choices=STATUS)
    ref_number = models.CharField(max_length=250, blank=True, null=True)
    grand_total = models.FloatField(default=0)
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="receipts")
    source = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="receipts")
    recvd_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receipts", blank=True, null=True)
    comitted_payment_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'PROC_Receipt'


class ReceiptLineItem(BaseModel):
    lot_number = models.CharField(max_length=100)
    exp_date= models.DateField(blank=True, null=True)
    recpt_qty = models.FloatField(default=0)
    per_pack_qty = models.FloatField(default=0)
    price = models.FloatField(default=0)
    commi = models.FloatField(default=0)
    reciept_identity = models.CharField(max_length=100)
    total_amt = models.FloatField(default=0)
    
    recpt = models.ForeignKey(Receipt, on_delete=models.CASCADE,blank=True, related_name='receipt_line_items')
    item = models.ForeignKey(Item, models.CASCADE, related_name="receipt_line_items")
    unit = models.ForeignKey(UOM, on_delete=models.CASCADE, blank=True, null=True, related_name="receipt_line_items")
    
    class Meta:
        db_table = 'PROC_Receipt_Line_Item'
        
    def save(self, *args, **kwargs):
        self.reciept_identity = generate_stock_identity(self.unit.id, self.lot_number,self.per_pack_qty, self.exp_date)
        super().save(*args, **kwargs)
        
