from django.urls import path
from apps.customers.views.customer import CustomerView, CustomerDetailsView

urlpatterns = [

    # Customer Urls
    path("customer/<int:pk>/", CustomerDetailsView.as_view()),
    path("customer/", CustomerView.as_view()),

    
]
