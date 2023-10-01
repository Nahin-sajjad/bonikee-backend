from django.db import models

from apps.share.models.base_model import BaseModel

from apps.sales.models.invoice import Invoice, InvoiceLineItem


class SaleReturn(BaseModel):
    inv = models.ForeignKey(
        Invoice, related_name="sale_return", blank=True, null=True, on_delete=models.CASCADE)
    ret_dt = models.DateTimeField()
    ref = models.CharField(max_length=100, blank=True, null=True)
    ret_amount = models.FloatField(default=0)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "SA_Sale_Return"


class SaleReturnLineItem(BaseModel):
    sale_ret = models.ForeignKey(
        SaleReturn, related_name="sale_return_line_items", blank=True, null=True, on_delete=models.CASCADE)
    inv_item = models.ForeignKey(
        InvoiceLineItem, related_name="sale_return_line_items", blank=True, null=True, on_delete=models.CASCADE)
    ret_qty = models.PositiveBigIntegerField(default=0)
    ret_amount = models.FloatField(default=0)

    class Meta:
        db_table = "SA_Sale_Return_Line_Item"
