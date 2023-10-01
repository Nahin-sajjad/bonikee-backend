from django.urls import path
from apps.vendors.views.vendor import VendorView, VendorDetailsView

urlpatterns = [
    path("", VendorView.as_view(), name="vendor-list"),
    path("<int:pk>/", VendorDetailsView.as_view(), name="vendor-details"),
]