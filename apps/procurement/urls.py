from django.urls import path
from apps.procurement.views.bill import BillPayView,BillPayDetailView
from apps.procurement.views.receipt import ReceiptView,ReceiptDetailsView,ReceiptLineItemView
from apps.procurement.views.pur_return import PurReturnView,PurReturnDetailView

urlpatterns = [
    #Bill Pay
    path('billpay/', BillPayView.as_view(), name="bill-pay-list"),
    path('billpay/<int:pk>/', BillPayDetailView.as_view(), name="bill-pay-details"),
    
    # Receipt
    path("receipt/", ReceiptView.as_view(), name="receipts"),
    path("receipt/<int:pk>/", ReceiptDetailsView.as_view(), name="receipt-details"),
    path("receipt/line/<int:pk>/", ReceiptLineItemView.as_view(), name="receipt-line-details"),
    
    #Retrun
    path("return/", PurReturnView.as_view(), name="returns"),
    path("return/<int:pk>/", PurReturnDetailView.as_view(), name="return-details"),
]
