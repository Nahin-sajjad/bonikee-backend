from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.procurement.serializers.pur_return import (
    PurReturnSerializer,
    PurRetLineItemSerializer,
)
from apps.procurement.models.pur_return import PurReturn

from apps.share.views import get_tenant_user, number_generate
from apps.share.services.stock_common import stock_exists
from apps.share.services.transaction_manager import TransactionManager

from datetime import datetime


class PurReturnView(generics.ListCreateAPIView):
    """
    API view for creating and listing PurReturn instances.
    """

    queryset = PurReturn
    serializer_class = PurReturnSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        """
        Retrieve the queryset of PurReturn instances for the current tenant.
        """
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            pur_return = tenant.purreturn_base_models.all()
            return pur_return

        else:
            print("Permission denied")

    def create(self, request, *args, **kwargs):
        """
        Create a PurReturn instance with associated transactions and line items.
        """
        tenant = get_tenant_user(self).tenant
        data = request.data
        try:
            last_pur_return = tenant.purreturn_base_models.last()
            previous_number = last_pur_return.return_num
        except:
            previous_number = f"PUR_RET-{datetime.now().year}-{0}"

        data["return_num"] = number_generate(previous_number=previous_number)
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            with transaction.atomic():
                try:
                    pur_return = serializer.save(tenant=tenant)
                    for item in data["pur_return_line_items"]:
                        stock_exists(
                            tenant,
                            data["source"],
                            item["reciept_identity"],
                            item["item"],
                            item["unit"],
                            (-int(item["return_qty"])),
                            item["lot_number"],
                            item["exp_date"],
                            item["per_pack_qty"],
                            0,
                            0,
                            0,
                        )
                    transaction_manage = TransactionManager(
                        tenant=tenant, tran_number=data["return_num"]
                    )

                    transaction_manage.transaction_create_or_update(
                        tran_group=102,
                        amount=data["return_amt"],
                        tran_type=1006,
                        tran_head=2,
                    )
                    pur_return_line_item_serializer = PurRetLineItemSerializer(
                        data=data["pur_return_line_items"], many=True
                    )
                    if pur_return_line_item_serializer.is_valid():
                        pur_return_line_item_serializer.save(
                            tenant=tenant, pur_retrn=pur_return
                        )
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    transaction.set_rollback(True)  # Rollback the transaction
                    return Response(
                        str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurReturnDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a PurReturn instance.
    """

    serializer_class = PurReturnSerializer
    queryset = PurReturn
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def update(self, request, pk):
        """
        Update a PurReturn instance, its transactions, and update associated stock quantities.
        """

    queryset = PurReturn
    serializer_class = PurReturnSerializer
    permission_classes = (GroupPermission,)

    def update(self, request, pk):
        tenant = get_tenant_user(self).tenant
        pur_return = tenant.purreturn_base_models.get(id=pk)
        pur_return_item_objects = pur_return.pur_return_line_items.all()
        serializer = self.get_serializer(pur_return, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    serializer.save()
                    transaction_manage = TransactionManager(
                        tenant=tenant, tran_number=request.data["return_num"]
                    )

                    transaction_manage.transaction_create_or_update(
                        tran_group=102,
                        amount=request.data["return_amt"],
                        tran_type=1006,
                        tran_head=2,
                    )

                    for item in request.data["pur_return_line_items"]:
                        try:
                            if item["qtyCng"]:
                                stock_exists(
                                    tenant=tenant,
                                    recvd_stock_id=pur_return.recpt.source.id,
                                    production_identity=item["reciept_identity"],
                                    item_id=item["item"],
                                    uom_id=item["unit"],
                                    recvd_qty=item["qtyCng"],
                                    lot_number=item["lot_number"],
                                    exp_date=item["exp_date"],
                                    per_pack_qty=item["per_pack_qty"],
                                    non_pack_qty=0,
                                    last_unit_price=item["unit_price"],
                                    date=pur_return.recpt.recpt_dt,
                                )
                        except KeyError:
                            pass
                        r_item = pur_return_item_objects.get(id=item["id"])
                        pur_return_line_item_serializer = PurRetLineItemSerializer(
                            r_item, data=item
                        )
                        if pur_return_line_item_serializer.is_valid():
                            pur_return_line_item_serializer.save()
                except Exception as e:
                    transaction.set_rollback(True)  # Rollback the transaction
                    return Response(
                        str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a PurReturn instance and associated stock entries.
        """
        tenant = get_tenant_user(self).tenant
        pk = kwargs.get("pk")
        pur_return = tenant.purreturn_base_models.get(id=pk)
        pur_return_line_items = pur_return.pur_return_line_items.all()
        with transaction.atomic():
            try:
                transaction_manage = TransactionManager(
                    tenant=tenant, tran_number=pur_return.return_num
                )

                transaction_manage.transaction_create_or_update(
                    tran_group=102, amount=0, tran_type=1006, tran_head=2
                )
                for item in pur_return_line_items:
                    stock_exists(
                        tenant=tenant,
                        recvd_stock_id=pur_return.recpt.source.id,
                        production_identity=item.recpt_item.reciept_identity,
                        item_id=item.recpt_item.item.id,
                        uom_id=item.recpt_item.unit.id,
                        recvd_qty=item.return_qty,
                        lot_number=item.recpt_item.lot_number,
                        exp_date=item.recpt_item.exp_date,
                        per_pack_qty=item.recpt_item.per_pack_qty,
                        non_pack_qty=0,
                        last_unit_price=item.recpt_item.price,
                        date=pur_return.recpt.recpt_dt,
                    )
                    item.delete()
                return super().destroy(request, *args, **kwargs)
            except Exception as e:
                transaction.set_rollback(True)  # Rollback the transaction
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
