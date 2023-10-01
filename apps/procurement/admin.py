from django.contrib import admin
from apps.procurement.models.bill import BillPay,BillPayLineItem
from apps.procurement.models.pur_return import PurReturn,PurReturnLineItem
from apps.procurement.models.receipt import Receipt,ReceiptLineItem

# Register your models here.
admin.site.register(BillPay)
admin.site.register(BillPayLineItem)
admin.site.register(PurReturn)
admin.site.register(PurReturnLineItem)
admin.site.register(Receipt)
admin.site.register(ReceiptLineItem)