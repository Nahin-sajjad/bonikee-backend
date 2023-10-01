from django.db import models
from apps.share.models.base_model import BaseModel
from apps.inventories.models.item import Item


class StockPrice(BaseModel):
    # stock = models.ForeignKey(Stock, related_name='stock_stock_price',
    #                           blank=True, null=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='item_stock_price',
                              blank=True, null=True, on_delete=models.CASCADE)
    markup = models.FloatField(default=0)
    mark_down = models.FloatField(default=0)
    sales_price = models.FloatField(default=0)
    min_price = models.FloatField(default=0)

    class Meta:
        db_table = 'INV_Stock_Price'
