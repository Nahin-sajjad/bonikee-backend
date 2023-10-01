from django.urls import path
from apps.finance.views.transaction import TransactionView, TransactionDetailsView
from apps.finance.views.inc_exp_type import IncExpTypeView
from apps.finance.views.inc_exp import IncExpView, IncExpDetailView
from apps.finance.views.customer_receivable import CustomerReceivableView, CustomerReceivableDetailsView
from apps.finance.views.customer_collection import CustomerCollectionView, CustomerCollectionDetailsView
from apps.finance.views.vendor_payable import VendorPayableView, VendorPayableDetailView
from apps.finance.views.vendor_pay import VendorPayView, VendorPayDetailView

urlpatterns = [
    path("customer-receivable/", CustomerReceivableView.as_view()),
    path("customer-receivable/<int:pk>/",
         CustomerReceivableDetailsView.as_view()),

    path("customer-collection/", CustomerCollectionView.as_view()),
    path("customer-collection/<int:pk>/",
         CustomerCollectionDetailsView.as_view()),

    path("income/expense/", IncExpView.as_view()),
    path("income/expense/<int:pk>/", IncExpDetailView.as_view()),

    path("income/expense/type/", IncExpTypeView.as_view()),

    path("transaction/", TransactionView.as_view()),
    path("transaction/<int:pk>/", TransactionDetailsView.as_view()),

    path("vendor/pay/", VendorPayView.as_view()),
    path("vendor/pay/<int:pk>/", VendorPayDetailView.as_view()),

    path("vendor/payable/", VendorPayableView.as_view()),
    path("vendor/payable/<int:pk>/", VendorPayableDetailView.as_view()),
]
