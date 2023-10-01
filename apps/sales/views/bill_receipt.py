from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.sales.models.bill_receipt import BillReceipt
from apps.sales.serializers.bill_receipt import (
    BillReceiptSerializer,
    BillReceiptLineItemSerializer,
)

from apps.share.views import get_tenant_user, number_generate
from apps.share.views import get_tenant_user
from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime


class BillReceiptView(generics.ListCreateAPIView):
    """
    API view for listing and creating BillReceipts.
    """

    queryset = BillReceipt
    serializer_class = BillReceiptSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Get the queryset of BillReceipts for the current tenant.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            bill_receipt_list = tenant.billreceipt_base_models.all().order_by(
                "-created_at"
            )
            return bill_receipt_list
        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        """
        Create a new BillReceipt and update related objects.
        """
        tenant = get_tenant_user(self).tenant
        data = request.data
        try:
            last_bill = tenant.billreceipt_base_models.last()
            previous_number = last_bill.bill_recpt_num
        except:
            previous_number = f"SA_BILL-{datetime.now().year}-{0}"

        data["bill_recpt_num"] = number_generate(previous_number=previous_number)
        inv = tenant.invoice_base_models.get(id=data["inv"])

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # with transaction.atomic():
            #     try:
            bill_receipt = serializer.save(tenant=tenant)
            bill_receipt_line_items = request.data["bill_receipt_line_items"]
            for item in bill_receipt_line_items:
                item["bill_receipt"] = bill_receipt.id
            bill_line_item_serializer = BillReceiptLineItemSerializer(
                data=bill_receipt_line_items, many=True
            )

            if bill_line_item_serializer.is_valid():
                bill_line_item_serializer.save(tenant=tenant, bill_receipt=bill_receipt)

            inv.status = data["status"]
            inv.paid_amount += int(data["recpt_amt"])
            inv.save()
            transaction_manage = TransactionManager(
                tenant=tenant, tran_number=bill_receipt.bill_recpt_num
            )

            transaction_manage.transaction_create_or_update(
                tran_group=102,
                amount=data["adv_amt"],
                tran_type=1002,
                tran_head=1,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # except Exception as e:
        #     transaction.set_rollback(True)  # Rollback the transaction
        #     return Response(
        #         str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillReceiptDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a BillReceipt.
    """

    queryset = BillReceipt
    serializer_class = BillReceiptSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, *args, **kwargs):
        """
        Update a BillReceipt and related objects.
        """
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")
        bill_recpt = tenant.billreceipt_base_models.get(id=pk)
        serializer = self.get_serializer(bill_recpt, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    inv = tenant.invoice_base_models.get(id=request.data["inv"])
                    if request.data["total_amount"] == request.data["paid_amount"]:
                        inv.status = 3
                    inv.paid_amount = request.data["paid_amount"]
                    inv.save()
                    transaction_manage = TransactionManager(
                        tenant=tenant, tran_number=bill_recpt.bill_recpt_num
                    )

                    transaction_manage.transaction_create_or_update(
                        tran_group=102,
                        amount=request.data["paid_amount"],
                        tran_type=1002,
                        tran_head=1,
                    )
                    return super().update(request, *args, **kwargs)
                except Exception as e:
                    transaction.set_rollback(True)  # Rollback the transaction
                    return Response(
                        str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a BillReceipt and update related transactions.
        """
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")
        bill_recpt = tenant.billreceipt_base_models.get(id=pk)
        transaction_manage = TransactionManager(
            tenant=tenant, tran_number=bill_recpt.bill_recpt_num
        )

        transaction_manage.transaction_create_or_update(
            tran_group=102, amount=0, tran_type=1002, tran_head=1
        )
        return super().destroy(request, *args, **kwargs)
