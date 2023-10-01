from django.contrib import admin
from apps.sales.models.invoice import Invoice, InvoiceLineItem
from apps.sales.models.challan import Challan, ChallanLineItem
from apps.sales.models.sale_return import SaleReturn, SaleReturnLineItem
from apps.sales.models.bill_receipt import BillReceipt, BillReceiptLineItem


# Register your models here.
admin.site.register(Invoice)
admin.site.register(InvoiceLineItem)
admin.site.register(Challan)
admin.site.register(ChallanLineItem)
admin.site.register(SaleReturn)
admin.site.register(SaleReturnLineItem)
admin.site.register(BillReceipt)
admin.site.register(BillReceiptLineItem)
