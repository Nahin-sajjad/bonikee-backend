from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.procurement.models.bill import BillPay
from apps.procurement.serializers.bill import BillPaySerializer, BillLineItemSerializer

from apps.share.views import get_tenant_user, number_generate
from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime


class BillPayView(generics.ListCreateAPIView):
    """
    API view for creating and listing BillPay instances.
    """

    queryset = BillPay
    serializer_class = BillPaySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Retrieve the queryset of BillPay instances for the current tenant.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            billpay = tenant.billpay_base_models.all().order_by("-created_at")
            return billpay

        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        """
        Create a BillPay instance with associated transactions and line items.
        """
        tenant = get_tenant_user(self).tenant
        data = request.data
        try:
            last_bill = tenant.billpay_base_models.last()
            previous_number = last_bill.bill_num
        except:
            previous_number = f"PUR_BILL-{datetime.now().year}-{0}"

        data["bill_num"] = number_generate(previous_number=previous_number)
        recpt = tenant.receipt_base_models.get(id=data["recpt"])
        bill = tenant.billpay_base_models.filter(recpt=recpt).last()
        new_paid = int(data["adv_amt"]) - bill.adv_amt
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    transaction_manage = TransactionManager(
                        tenant=tenant, tran_number=data["bill_num"]
                    )

                    transaction_manage.transaction_create_or_update(
                        tran_group=103, amount=new_paid, tran_type=1004, tran_head=2
                    )
                    bill_pay = serializer.save(tenant=tenant, status=data["status"])
                    pay_line_items = request.data["pays_line_items"]
                    for item in pay_line_items:
                        item["bill"] = bill_pay.id
                    bill_line_item_serializer = BillLineItemSerializer(
                        data=pay_line_items, many=True
                    )

                    if bill_line_item_serializer.is_valid():
                        bill_line_item_serializer.save(tenant=tenant, bill=bill_pay)
                    if data["status"] == 2:
                        recpt.status = 2
                        recpt.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    transaction.set_rollback(True)  # Rollback the transaction
                    return Response(
                        str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillPayDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a BillPay instance.
    """

    queryset = BillPay
    serializer_class = BillPaySerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, *args, **kwargs):
        """
        Update a BillPay instance, its transactions, and update associated Receipt status.
        """
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")
        bill_pay = tenant.billpay_base_models.get(id=pk)
        with transaction.atomic():
            try:
                transaction_manage = TransactionManager(
                    tenant=tenant, tran_number=request.data["bill_num"]
                )

                transaction_manage.transaction_create_or_update(
                    tran_group=103,
                    amount=request.data["bill_amt"],
                    tran_type=1004,
                    tran_head=2,
                )
                if request.data["status"] == 2:
                    bill_pay.status = 2
                    bill_pay.save()
                    recpt = tenant.receipt_base_models.get(id=request.data["recpt"])
                    recpt.status = 2
                    recpt.save()
                return super().update(request, *args, **kwargs)
            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a BillPay instance and associated transactions.
        """
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")
        bill_pay = tenant.billpay_base_models.get(id=pk)
        with transaction.atomic():
            try:
                return super().destroy(request, *args, **kwargs)
            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
