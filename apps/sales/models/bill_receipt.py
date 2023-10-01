from django.db import models

from apps.share.models.base_model import BaseModel

from apps.sales.models.invoice import Invoice, InvoiceLineItem


class BillReceipt(BaseModel):
    inv = models.ForeignKey(
        Invoice, related_name="bill_receipts", blank=True, null=True, on_delete=models.CASCADE)
    recpt_dt = models.DateTimeField()
    pay_method = models.CharField(max_length=100)
    recpt_amt = models.FloatField(default=0)
    bill_recpt_num = models.CharField(max_length=100)

    class Meta:
        db_table = "SA_Bill_Receipt"


class BillReceiptLineItem(BaseModel):
    bill_receipt = models.ForeignKey(
        BillReceipt, related_name="bill_receipt_line_items", blank=True, null=True, on_delete=models.CASCADE)
    inv_item = models.ForeignKey(
        InvoiceLineItem, related_name="bill_receipt_line_items", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = "SA_Bill_Receipt_Line_Item"
