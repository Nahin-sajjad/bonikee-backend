from django.db import models
from apps.share.models.base_model import BaseModel
from apps.share.views import generate_stock_identity
from apps.inventories.models.item import Item
from apps.inventories.models.stock_price import StockPrice
from apps.inventories.models.uom import UOM
from apps.inventories.models.warehouse import Warehouse


class Stock(BaseModel):
    stock_identity = models.CharField(max_length=250, blank=True, null=True)
    lot_number = models.CharField(max_length=20, blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    last_recvd_date = models.DateTimeField(blank=True, null=True)
    # unit_price = models.FloatField(default=0)

    # pack_qty = models.FloatField(default=0)
    per_pack_qty = models.FloatField(default=0)
    non_pack_qty = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    source = models.ForeignKey(
        Warehouse, related_name='stocks', on_delete=models.CASCADE)
    # product = models.ForeignKey(Item, related_name="stocks", on_delete=models.CASCADE)
    item = models.ForeignKey(
        Item, related_name="stocks", on_delete=models.CASCADE)
    item_price = models.ForeignKey(
        StockPrice, related_name="stocks", on_delete=models.CASCADE, blank=True, null=True)
    uom = models.ForeignKey(UOM, blank=True, null=True,
                            related_name="stocks", on_delete=models.SET_NULL)
    # pack_uom = models.ForeignKey(
    #     UOM, blank=True, null=True, related_name="pack_stocks", on_delete=models.SET_NULL)

    class Meta:
        db_table = 'INV_Stock'

    def save(self, *args, **kwargs):
        self.stock_identity = generate_stock_identity(
            self.uom.id, self.lot_number, self.per_pack_qty, self.exp_date)
        super().save(*args, **kwargs)
