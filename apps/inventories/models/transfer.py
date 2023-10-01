
from django.db import models
from apps.share.models.base_model import BaseModel
from apps.inventories.models.stock import Stock
from apps.inventories.models.uom import UOM
from apps.inventories.models.warehouse import Warehouse

 
class Transfer(BaseModel):
    transfer_no = models.IntegerField(default=0)
    from_stk = models.ForeignKey(Warehouse, related_name="from_warehouse_transfers", on_delete=models.CASCADE)
    to_stk = models.ForeignKey(Warehouse, related_name="to_warehouse_transfers", on_delete=models.CASCADE)
    trans_dt = models.DateField(auto_now=True)
    PURPOSE = (
        (1,'Production'),
        (2, 'Sale')
    )
    purpose_cd = models.SmallIntegerField(choices=PURPOSE, blank=True, null=True)

    class Meta:
        db_table = 'INV_Transfer'


class TransferItem(BaseModel):
    transfer = models.ForeignKey(Transfer, related_name="transfers", on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, related_name="transfer_item", on_delete=models.CASCADE)
    trans_qty = models.IntegerField(default=0)
    trans_unit = models.ForeignKey(UOM, related_name="transfer_unit", on_delete=models.CASCADE)
    des_stock_identity = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'INV_Transfer_Item'
