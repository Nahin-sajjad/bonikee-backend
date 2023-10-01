from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.finance.models.vendor_pay import VendorPay
from apps.finance.serializers.vendor_pay import VendorPaySerializer
from apps.share.views import get_tenant_user, number_generate
from datetime import datetime

from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime


class VendorPayView(generics.ListCreateAPIView):
    """
    View for listing and creating vendor payment records.

    Attributes:
        queryset (QuerySet): The queryset used to fetch VendorPay instances.
        serializer_class (Serializer): The serializer class for VendorPay objects.
    """

    queryset = VendorPay
    serializer_class = VendorPaySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset of VendorPay objects for the current tenant.

        Returns:
            QuerySet: Filtered queryset of VendorPay objects.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            vendor_pay = tenant.vendorpay_base_models.all().order_by("-created_at")
            return vendor_pay

        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        """
        Create a new vendor payment record and manage associated transactions.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: JSON response indicating the success or failure of the creation.
        """
        with transaction.atomic():
            try:
                tenant = get_tenant_user(self).tenant
                data = request.data
                try:
                    previous_number = tenant.vendorpay_base_models.last().pay_num
                except:
                    previous_number = f"VPAY-{datetime.now().year}-{0}"
                data["pay_num"] = number_generate(previous_number)
                serializer = self.get_serializer(data=data)

                # Create or update the transaction associated with the payment
                if serializer.is_valid():
                    serializer.save(tenant=tenant)
                    transaction_manage = TransactionManager(
                        tenant=tenant, tran_number=data["pay_num"]
                    )

                    transaction_manage.transaction_create_or_update(
                        tran_group=103, amount=data["amt"], tran_type=1010, tran_head=4
                    )

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorPayDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a specific vendor payment record.

    Attributes:
        queryset (QuerySet): The queryset used to fetch VendorPay instances.
        serializer_class (Serializer): The serializer class for VendorPay objects.
    """

    queryset = VendorPay
    serializer_class = VendorPaySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, *args, **kwargs):
        """
        Update a specific vendor payment record and manage associated transactions.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: JSON response indicating the success or failure of the update.
        """
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")

        # Create or update the transaction associated with the payment
        with transaction.atomic():
            try:
                vendor_pay = tenant.vendorpay_base_models.get(id=pk)
                transaction_manage = TransactionManager(
                    tenant=tenant, tran_number=vendor_pay.pay_num
                )
                transaction_manage.transaction_create_or_update(
                    tran_group=103,
                    amount=request.data["amt"],
                    tran_type=1010,
                    tran_head=4,
                )

                return super().update(request, *args, **kwargs)
            except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
