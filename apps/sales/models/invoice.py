from typing import Iterable, Optional
from django.db import models
from apps.share.models.base_model import BaseModel
from apps.inventories.models.stock import Stock
from apps.inventories.models.uom import UOM
from apps.inventories.models.warehouse import Warehouse
from apps.customers.models.customer import Customer

# from apps.share.views import generate_invoice_number


class Invoice(BaseModel):
    cust = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="invoices", null=True
    )
    bill_to = models.CharField(max_length=264, null=True, blank=True)
    warehouse = models.ForeignKey(
        Warehouse, related_name="invoice_stocks", on_delete=models.CASCADE
    )

    inv_num = models.CharField(max_length=100)
    inv_dt = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=100)
    comitted_payment_date = models.DateTimeField(blank=True, null=True)

    STATUS = (
        (1, "Open"),
        (2, "Partially Paid"),
        (3, "Fully Paid"),
        (4, "Cancelled"),
        (5, "Delivered"),
    )
    status = models.SmallIntegerField(choices=STATUS, default=1)

    discount_amount = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    paid_amount = models.FloatField(default=0)
    due_amount = models.FloatField(default=0)

    class Meta:
        db_table = "SA_Invoice"

    def __str__(self) -> str:
        return self.inv_num

    def save(self, *args, **kwargs):
        self.due_amount = self.total_amount - self.paid_amount
        super(Invoice, self).save(*args, **kwargs)


class InvoiceLineItem(BaseModel):
    inv = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="invoice_line_items"
    )

    item = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="invoice_line_items"
    )
    qty = models.FloatField(default=0)
    unit = models.ForeignKey(
        UOM, on_delete=models.CASCADE, related_name="invoice_line_items"
    )
    per_pack_qty = models.FloatField(default=0)
    price = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    disc = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    class Meta:
        db_table = "SA_Invoice_Line_Item"
