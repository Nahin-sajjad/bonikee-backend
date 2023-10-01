
from django.db import models
from apps.share.models.base_model import BaseModel
from apps.inventories.models.item import Item
from apps.inventories.models.uom import UOM
from apps.inventories.models.warehouse import Warehouse
from apps.users.models import User
from apps.share.views import generate_stock_identity


class Production(BaseModel):
    production_identity = models.CharField(
        max_length=100, blank=True, null=True)

    exp_date = models.DateField(blank=True, null=True)
    recvd_date = models.DateField(blank=True, null=True)
    recvd_qty = models.FloatField(default=0)
    # pack_qty = models.FloatField(default=0)
    # non_pack_qty = models.FloatField(default=0)
    per_pack_qty = models.FloatField(default=0)
    cost_per_unit = models.FloatField(default=0)
    lot_number = models.CharField(max_length=20, blank=True, null=True)
    sku = models.CharField(max_length=250, blank=True, null=True)

    item = models.ForeignKey(
        Item, related_name="item_productions", on_delete=models.CASCADE)
    uom = models.ForeignKey(UOM, related_name='uom_productions',
                            blank=True, null=True, on_delete=models.SET_NULL)
    # pack_uom = models.ForeignKey(
    #     UOM, related_name='uom_pack_productions', blank=True, null=True, on_delete=models.SET_NULL)
    recvd_by = models.ForeignKey(
        User, related_name='recvd_by_productions', blank=True, null=True, on_delete=models.SET_NULL)
    recvd_stock = models.ForeignKey(
        Warehouse, related_name='recvd_stock_productions', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'INV_Production'
        ordering = ('-id',)

    def __str__(self) -> str:
        return f'Received Stock - {self.recvd_stock.warehouse_name} & Lot Number-{self.lot_number}'

    def save(self, *args, **kwargs):
        self.production_identity = generate_stock_identity(
            self.uom.id, self.lot_number, self.per_pack_qty, self.exp_date)
        super().save(*args, **kwargs)
