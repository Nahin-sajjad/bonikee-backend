from django.contrib import admin
from apps.finance.models.transaction import Transaction
from apps.finance.models.inc_exp_type import IncExpType
from apps.finance.models.inc_exp import IncExp
from apps.finance.models.vendor_pay import VendorPay
from apps.finance.models.vendor_payable import VendorPayable
from apps.finance.models.customer_receivable import CustomerReceivable
from apps.finance.models.customer_collection import CustomerCollection


admin.site.register(Transaction)
admin.site.register(CustomerReceivable)
admin.site.register(CustomerCollection)
admin.site.register(IncExpType)
admin.site.register(IncExp)
admin.site.register(VendorPay)
admin.site.register(VendorPayable)
