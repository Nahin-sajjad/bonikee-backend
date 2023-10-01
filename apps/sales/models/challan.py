from django.db import models

from apps.share.models.base_model import BaseModel

from apps.inventories.models.stock import Stock
from apps.inventories.models.uom import UOM

from apps.sales.models.invoice import Invoice


class Challan(BaseModel):
    challan_number = models.CharField(max_length=100)
    challan_dt = models.DateTimeField()
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='challans', blank=True, null=True)

    class Meta:
        db_table = 'SA_Challan'


class ChallanLineItem(BaseModel):
    challan = models.ForeignKey(Challan, on_delete=models.CASCADE, related_name='challans_lineitem', blank=True, null=True)
    item = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name='challans_lineitem', blank=True, null=True)
    unit = models.ForeignKey(
        UOM, on_delete=models.CASCADE, related_name='challans_lineitem', blank=True, null=True)

    qty = models.BigIntegerField(default=0)
    per_pack_qty = models.BigIntegerField(default=0)
    price = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    disc = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    class Meta:
        db_table = 'SA_Challan_Line_Item'
