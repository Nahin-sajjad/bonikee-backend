from django.db import models
from apps.share.models.base_model import BaseModel
from apps.inventories.models.item import Item


class Adjust(BaseModel):
    ADJUSTMENT_CHOICES = [
        (1, "Increament"),
        (2, "Decreament"),
    ]

    adjust_type_cd = models.CharField(
        max_length=100, choices=ADJUSTMENT_CHOICES)
    adjust_dt = models.DateField(auto_now=True)
    adjust_qty = models.FloatField(default=0)
    reason_cd = models.SmallIntegerField(default=0)
    reason = models.TextField(blank=True, null=True)
    item = models.ForeignKey(
        Item, related_name="adjusts", on_delete=models.CASCADE)

    class Meta:
        db_table = 'INV_Adjust'
