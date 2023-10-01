from django.urls import path
from apps.sales.views.invoice import InvoiceView, InvoiceDetailsView
from apps.sales.views.challan import ChallanView, ChallanDetailsView
from apps.sales.views.bill_receipt import BillReceiptView, BillReceiptDetailView
from apps.sales.views.sale_return import SaleReturnView, SaleReturnDetailsView

urlpatterns = [
    path("invoice/", InvoiceView.as_view(), name="invoice"),
    path("invoice/<int:pk>/", InvoiceDetailsView.as_view(), name="invoice_details"),

    path("challan/", ChallanView.as_view(), name="challan"),
    path("challan/<int:pk>/", ChallanDetailsView.as_view(), name="challan_details"),

    path("bill/receipt/", BillReceiptView.as_view(), name="bill_receipt"),
    path("bill/receipt/<int:pk>/", BillReceiptDetailView.as_view(),
         name="bill_receipt_details"),

    path("return/", SaleReturnView.as_view(), name="sale_return"),
    path("return/<int:pk>/", SaleReturnDetailsView.as_view(),
         name="sale_return_details")
]
