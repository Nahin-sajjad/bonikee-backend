from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.share.views import get_tenant_user, generate_stock_identity, number_generate
from apps.share.services.stock_common import stock_exists_obj

from apps.procurement.models.receipt import Receipt, ReceiptLineItem
from apps.procurement.serializers.receipt import (
    ReceiptSerializer,
    ReceiptLineItemSerializer,
)
from apps.procurement.serializers.bill import BillPaySerializer, BillLineItemSerializer

from datetime import datetime


class ReceiptView(generics.ListCreateAPIView):
    """
    API view for creating and listing Receipt instances.
    """

    queryset = Receipt
    serializer_class = ReceiptSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Retrieve the queryset of Receipt instances for the current tenant.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            receipt = user_tenant.tenant.receipt_base_models.all().exclude(status=2)
            return receipt
        else:
            raise Exception("Permission Denied!")

    def stock_obj(self, data, item, recpt):
        """
        Create a stock object for stock_exists_obj function.
        """
        obj = {
            "recvd_stock": data["source"],
            "item": item["item"],
            "recvd_qty": item["recpt_qty"],
            "recvd_date": recpt.recpt_dt,
            "cost_per_unit": item["price"],
            "lot_number": item["lot_number"],
            "exp_date": item["exp_date"],
            "per_pack_qty": item["per_pack_qty"],
            "uom": item["unit"],
        }
        return obj

    def create(self, request, *args, **kwargs):
        """
        Create a Receipt instance with associated transactions, bills, and line items.
        """
        tenant = get_tenant_user(self).tenant
        data = request.data
        with transaction.atomic():
            try:
                last_recpt = tenant.receipt_base_models.last()
                previous_number = last_recpt.recpt_num
            except:
                previous_number = f"PUR_REC-{datetime.now().year}-{0}"

        recpt_num = number_generate(previous_number=previous_number)
        recvd_by = request.user
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    recpt = serializer.save(
                        tenant=tenant, recpt_num=recpt_num, recvd_by=recvd_by
                    )
                    try:
                        last_bill = tenant.billpay_base_models.last()
                        previous_number = last_bill.bill_num
                    except:
                        previous_number = f"PUR_RECPT-{datetime.now().year}-{0}"
                    bill_data = {
                        "bill_num": number_generate(previous_number=previous_number),
                        "pay_method": 1,
                        "bill_amt": data["grand_total"],
                        "recpt": recpt.id,
                    }
                    bill_Pay_serializer = BillPaySerializer(data=bill_data)  # type: ignore
                    if bill_Pay_serializer.is_valid():
                        bill_pay = bill_Pay_serializer.save(tenant=tenant)

                    bill_pay_line_item_data = []

                    for item in data["receipt_line_items"]:
                        item["reciept_identity"] = generate_stock_identity(
                            item["unit"],
                            item["lot_number"],
                            item["per_pack_qty"],
                            item["exp_date"],
                        )
                        stock_obj = self.stock_obj(data, item, recpt)
                        stock_exists_obj(tenant, stock_obj, item["reciept_identity"])
                    recpt_line_item_serializer = ReceiptLineItemSerializer(
                        data=data["receipt_line_items"], many=True
                    )

                    if recpt_line_item_serializer.is_valid():
                        recpt_line_item_serializer.save(tenant=tenant, recpt=recpt)

                        for recpt_line_item in recpt_line_item_serializer.instance:
                            bill_pay_line_item = {
                                "bill": bill_pay.id,
                                "recpt_item": recpt_line_item.id,
                            }
                            bill_pay_line_item_data.append(bill_pay_line_item)
                        bill_pay_line_item_serializer = BillLineItemSerializer(
                            data=bill_pay_line_item_data, many=True
                        )
                        if bill_pay_line_item_serializer.is_valid():
                            bill_pay_line_item_serializer.save(tenant=tenant)

                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    transaction.set_rollback(True)  # Rollback the transaction
                    return Response(
                        str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiptDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a Receipt instance.
    """

    queryset = Receipt
    serializer_class = ReceiptSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def stock_obj(self, data, item, recpt):
        """
        Create a stock object for stock_exists_obj function during update.
        """
        obj = {
            "recvd_stock": data["source"],
            "item": item["item"],
            "recvd_qty": item["qtyCng"],
            "recvd_date": recpt.recpt_dt,
            "cost_per_unit": item["price"],
            "lot_number": item["lot_number"],
            "exp_date": item["exp_date"],
            "per_pack_qty": item["per_pack_qty"],
            "uom": item["unit"],
        }
        return obj

    def update(self, request, pk):
        """
        Update a Receipt instance, its transactions, bills, and update associated stock quantities.
        """
        tenant = get_tenant_user(self).tenant
        receipt = tenant.receipt_base_models.get(id=pk)
        receipt_item_objects = receipt.receipt_line_items.all()
        serializer = self.get_serializer(receipt, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    recpt = serializer.save()
                    bill_pays = receipt.bill_pays.all()
                    for bill in bill_pays:
                        bill.bill_amt = request.data["grand_total"]
                        bill.save()
                    for item in request.data["receipt_line_items"]:
                        with transaction.atomic():
                            try:
                                if item["qtyCng"]:
                                    stock_obj = self.stock_obj(
                                        request.data, item, recpt
                                    )
                                    stock_exists_obj(
                                        tenant, stock_obj, item["reciept_identity"]
                                    )
                            except KeyError:
                                pass

                        r_item = receipt_item_objects.get(id=item["id"])
                        recpt_line_item_serializer = ReceiptLineItemSerializer(
                            r_item, data=item
                        )

                        if recpt_line_item_serializer.is_valid():
                            recpt_line_item_serializer.save()
                except Exception as e:
                    transaction.set_rollback(True)  # Rollback the transaction
                    return Response(
                        str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """
        Delete a Receipt instance, its line items, and update associated stock quantities.
        """
        tenant = get_tenant_user(self).tenant
        receipt = tenant.receipt_base_models.get(id=pk)
        receipt_item_objects = receipt.receipt_line_items.all()
        bill_pays = receipt.bill_pays.all()
        with transaction.atomic():
            try:
                for item in receipt_item_objects:
                    pays_line_item = item.pays_line_items.all()
                    obj = {
                        "recvd_stock": receipt.source.id,
                        "item": item.item.id,
                        "recvd_qty": (-item.recpt_qty),
                        "recvd_date": receipt.recpt_dt,
                        "cost_per_unit": item.price,
                        "lot_number": item.lot_number,
                        "exp_date": item.exp_date,
                        "per_pack_qty": item.per_pack_qty,
                        "uom": item.unit.id,
                    }
                    stock_exists_obj(tenant, obj, item.reciept_identity)
                    pays_line_item.delete()
                    item.delete()
                for bill in bill_pays:
                    bill.delete()
                receipt.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptLineItemView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a ReceiptLineItem instance.
    """

    serializer_class = ReceiptLineItemSerializer
    queryset = ReceiptLineItem

    def destroy(self, request, pk):
        """
        Delete a ReceiptLineItem instance and update associated stock quantities.
        """
        tenant = get_tenant_user(self).tenant
        receipt_line_item = tenant.receiptlineitem_base_models.get(id=pk)
        with transaction.atomic():
            try:
                pays_line_item = receipt_line_item.pays_line_items.all()
                obj = {
                    "recvd_stock": receipt_line_item.recpt.source.id,
                    "item": receipt_line_item.item.id,
                    "recvd_qty": (-receipt_line_item.recpt_qty),
                    "recvd_date": receipt_line_item.created_at,
                    "cost_per_unit": receipt_line_item.price,
                    "lot_number": receipt_line_item.lot_number,
                    "exp_date": receipt_line_item.exp_date,
                    "per_pack_qty": receipt_line_item.per_pack_qty,
                    "uom": receipt_line_item.unit.id,
                }
                stock_exists_obj(tenant, obj, receipt_line_item.reciept_identity)
                pays_line_item.delete()
                receipt_line_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
